import bpy.utils.previews
from pathlib import Path


_icons = {}


def register():
    global _icons
    _icons = bpy.utils.previews.new()
    icons_dir = Path(__file__).parent / "images"
    _icons.load(
        name="search", 
        path=str(icons_dir / "icon_search.png"), 
        path_type="IMAGE")


def unregister():
    bpy.utils.previews.remove(_icons)


def get_search_id():
    return _icons["search"].icon_id