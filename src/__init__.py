bl_info = {
    "name": "Edit Instanced Collection",
    "description": "Quickly find the instanced collection source",
    "author": "Lukas Sabaliauskas <lukas_sabaliauskas@hotmail.com>",
    "version": (0, 0, 1),
    "blender": (4, 0, 0),
    "location": "Object Properties > Instancing",
    # "doc_url": "https://extensions.blender.org/add-ons/",
    # "tracker_url": "https://github.com/Trukasss/",
}

import bpy
from bpy.types import Operator, Context, Object, Collection, Panel


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
        # Link to scene if necessary
        is_linked = False
        if coll not in context.scene.collection.children_recursive:
            context.scene.collection.children.link(coll)
            is_linked = True
        # Select collection's objects
        for obj in context.selected_objects:
            obj: Object
            obj.select_set(False)
        for obj in coll.all_objects:
            obj.select_set(True)
        # Try frame selection
        frame_selected()
        self.report({"INFO"}, f"Found source collection '{coll.name}'" + (" and linked it to scene" if is_linked else ""))
        return {"FINISHED"}


def draw_operator(self, context: Context):
    if is_collection_instance(context.object):
        layout = self.layout
        layout.operator(EIC_OT_ShowSource.bl_idname, icon="ZOOM_ALL")


def register():
    bpy.utils.register_class(EIC_OT_ShowSource)
    bpy.types.OBJECT_PT_instancing.append(draw_operator)


def unregister():
    bpy.types.OBJECT_PT_instancing.remove(draw_operator)
    bpy.utils.unregister_class(EIC_OT_ShowSource)