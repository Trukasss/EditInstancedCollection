bl_info = {
    "name": "Edit Instanced Collection",
    "description": "Quickly find the instanced collection source",
    "author": "Lukas Sabaliauskas <lukas_sabaliauskas@hotmail.com>",
    "version": (0, 0, 3),
    "blender": (4, 0, 0),
    "location": "Object Properties > Instancing",
    # "doc_url": "https://extensions.blender.org/add-ons/",
    # "tracker_url": "https://github.com/Trukasss/",
}

import bpy
from bpy.types import Operator, Context, Object, Collection, LayerCollection, Scene, ViewLayer
import importlib

from . import icons
importlib.reload(icons)


def is_collection_instance(object: Object):
    if object and object.type == "EMPTY" and object.instance_type == "COLLECTION":
        return True
    return False


def frame_selected():
    if not bpy.context.selected_objects:
        return
    window = bpy.context.window
    screen = window.screen
    area_3d = next((a for a in screen.areas if a.type == 'VIEW_3D'), None)
    if not area_3d:
        return
    region = next((r for r in area_3d.regions if r.type == 'WINDOW'), None)
    if not region:
        return
    with bpy.context.temp_override(window=window, area=area_3d, region=region):
        bpy.ops.view3d.view_selected(use_all_regions=True)


def recursive_layer_collection_search(collection: Collection, layer_collections: bpy.types.CollectionProperty):
    for lc in layer_collections:
        lc: LayerCollection
        if lc.collection == collection:
            return lc
    for lc in layer_collections:
        found = recursive_layer_collection_search(collection, lc.children)
        if found:
            return lc
    return None


class EIC_OT_ShowSource(Operator):
    """Show collection instance's source"""
    bl_idname = "eic.show_source"
    bl_label = "Show instance source"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context):
        cls.poll_message_set("Must select collection instance")
        return is_collection_instance(context.object)
    
    def execute(self, context: Context):
        # Find source collection
        if not is_collection_instance(context.object):
            self.report({"ERROR"}, f"Selected object must be a collection instance")
            return {"CANCELLED"}
        coll = context.object.instance_collection
        coll: Collection
        if not coll:
            self.report({"WARNING"}, f"Missing collection instance source")
            return {"CANCELLED"}
        msg = f"Found source '{coll.name}'"

        # Find scene
        scene = next((s for s in bpy.data.scenes if coll in s.collection.children_recursive), None)
        is_new_scene = False
        if not scene:
            scene = bpy.data.scenes.new(f"({coll.name})")
            scene.collection.children.link(coll)
            is_new_scene = True
        
        # Search view layers for already "checked" layer collection
        view_layer = None
        layer_coll = None
        for vl in scene.view_layers:
            vl: ViewLayer
            layer_coll = recursive_layer_collection_search(coll, vl.layer_collection.children)
            if layer_coll and layer_coll.exclude == False: # "checked"
                view_layer = vl
                break
        if layer_coll is None:
            raise ValueError(f"Missing layer collection in '{scene.name}'")
        if view_layer is None:
            if context.scene == scene:
                view_layer = context.view_layer
            else:
                view_layer = scene.view_layers[0]
        
        # Switch to scene & layer
        if context.window.scene == scene:
            msg += " > current scene"
        else:
            msg += f" > {'new' if is_new_scene else 'existing'} scene '{scene.name}'"
            context.window.scene = scene
        if context.window.view_layer == view_layer:
            msg += " > current view layer"
        else:
            msg += f" > view layer '{view_layer.name}'"
            context.window.view_layer = view_layer
        
        # Show and select source
        coll.hide_select = False
        coll.hide_viewport = False
        layer_coll.exclude = False
        view_layer.active_layer_collection = layer_coll
        for obj in scene.objects:
            obj: Object
            if obj.name in coll.all_objects:
                obj.select_set(True, view_layer=view_layer)
            else:
                obj.select_set(False, view_layer=view_layer)
        frame_selected()

        self.report({"INFO"}, msg)
        return {"FINISHED"}


def draw_operator(self, context: Context):
    if is_collection_instance(context.object):
        layout = self.layout
        layout.operator(EIC_OT_ShowSource.bl_idname, icon_value=icons.get_search_id())


def register():
    icons.register()
    bpy.utils.register_class(EIC_OT_ShowSource)
    bpy.types.OBJECT_PT_instancing.append(draw_operator)


def unregister():
    bpy.types.OBJECT_PT_instancing.remove(draw_operator)
    bpy.utils.unregister_class(EIC_OT_ShowSource)
    icons.unregister()