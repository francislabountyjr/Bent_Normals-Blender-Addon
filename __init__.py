# Copyright (C) 2022, Francis LaBounty, All rights reserved.

import bpy
import numpy as np

from . import bn_nodes

bl_info = {
    "name": "Bent Normals",
    "description": "Bakes bent normals using source normal and height textures.",
    "author": "Francis LaBounty - labounty3d@gmail.com - github.com/francislabountyjr",
    "version": (1, 0, 0),
    "category": "Node",
    "blender": (3, 00, 0),
    "location": "Shader Editor > Toolbar > Bent Normals",
    "wiki_url": "",
    "warning": "",
    "tracker_url": "",
    "support": "COMMUNITY"
}


class BN_OT_BakeBentNormals(bpy.types.Operator):
    """Bakes bent normals using existing normal and height maps"""

    bl_idname = "mesh.bn_bake_bent_normals"
    bl_label = "Bake Bent Normals"

    def execute(self, context):
        wm = context.window_manager

        # store original height and normal
        height_og = wm.Height
        normal_og = wm.Normal

        # copy pixels from the height image to a flattened float32 numpy array
        height_img = bpy.data.images[wm.Height]

        width, height = height_img.size
        channels = height_img.channels
        num_pixels = width * height * channels
        height_tex = np.zeros(num_pixels, dtype=np.float32)
        height_img.pixels.foreach_get(height_tex)

        # import bentnormals module
        import sys
        sys.path.append(
            context.preferences.addons['bent_normals'].preferences.module_dir)
        import bentnormals as bn

        # calculate bentnormals mask (returns flattened float32 numpy array)
        mask = bn.calculate_mask(height_tex.reshape((height, width, channels))[
                                 :, :, 0]*255.0, width, height, wm.ray_length, wm.ray_count, wm.tiled)

        # min-max scale mask to 0-1 range
        min = np.min(mask)
        max = np.max(mask)
        mask = (mask - min)/(max - min)

        # setup mask image in blender and then copy the pixel data from the mask array
        if wm.mask_name not in bpy.data.images.keys():
            bpy.data.images.new(wm.mask_name, width=width,
                                height=height, alpha=False, float_buffer=True)
        outputMask = bpy.data.images[wm.mask_name]
        try:
            outputMask.colorspace_settings.name = "non-color"
        except Exception as e:
            outputMask.colorspace_settings.name = "role_data"  # ACES-CG color space
        outputMask.pixels.foreach_set(mask)

        # restore original height and normal
        wm.Height = height_og
        wm.Normal = normal_og

        # setup bentnormals node group
        group = bn_nodes.BN_CreateBentNormalGroup(wm.mask_name)
        mask_node = bn_nodes.BN_NodeSearch(group.node_tree, "Mask")
        original_normal_node = bn_nodes.BN_NodeSearch(
            group.node_tree, "Original Normal")

        mask_node.image = outputMask

        original_normal_node.image = bpy.data.images[wm.Normal]
        try:
            bpy.data.images[wm.Normal].colorspace_settings.name = "non-color"
        except Exception as e:
            # ACES-CG color space
            bpy.data.images[wm.Normal].colorspace_settings.name = "role_data"

        return {"FINISHED"}


class BN_PT_Panel(bpy.types.Panel):
    """Create a panel in the shader editor tool shelf"""

    bl_label = "Bent Normals"
    bl_idname = "panel.bn_node_editor_panel"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Bent Normals"

    def draw(self, context):
        return


class BN_PT_CreatePanel(bpy.types.Panel):
    """Create sub panel"""

    bl_label = "Create Node"
    bl_idname = "panel.bn_node_editor_create_panel"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Bent Normals"
    bl_parent_id = "panel.bn_node_editor_panel"

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager

        row = layout.row(align=True)
        integrity_check = True

        if not wm.Normal or not wm.Height:
            integrity_check = False
            error_message = "Select Textures"

        if context.preferences.addons['bent_normals'].preferences.module_dir == '':
            integrity_check = False
            error_message = "Choose BN Module Dir in Addon Preferences"

        if integrity_check:
            row.operator("mesh.bn_bake_bent_normals",
                         icon="FILE_REFRESH", text="Bake Bent Normals")
        else:
            row.label(text=error_message, icon="ERROR")

        row = layout.row(align=True)
        row.prop(wm, "ray_count", text="Ray Count:")

        row = layout.row(align=True)
        row.prop(wm, "ray_length", text="Ray Length:")

        row = layout.row(align=True)
        row.prop(wm, "Normal")

        row = layout.row(align=True)
        row.prop(wm, "Height")

        row = layout.row(align=True)
        row.prop(wm, "mask_name", text="Mask Name")

        row = layout.row(align=True)
        row.prop(wm, "tiled", text="Tiled")


class BN_Preferences(bpy.types.AddonPreferences):
    """Create addon preferences"""

    bl_idname = __name__

    module_dir: bpy.props.StringProperty(
        name="Module Folder Path",
        subtype='DIR_PATH',
        default=""
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text='Directory where BN module is located')
        row = layout.row()
        row.prop(self, 'module_dir')


def enum_images_normal(self, context):
    """Normal EnumProperty callback"""
    image_enum_list = []

    if context is None:
        image_enum_list.append(('', '', "", "", 0))
        return image_enum_list

    for i, img in enumerate(bpy.data.images):
        image_enum_list.append((img.name, img.name, "", "", i))

    if len(image_enum_list) < 1:
        image_enum_list.append(('', '', "", "", 0))

    return image_enum_list


def enum_images_height(self, context):
    """Height EnumProperty callback"""
    image_enum_list = []

    if context is None:
        image_enum_list.append(('', '', "", "", 0))
        return image_enum_list

    for i, img in enumerate(bpy.data.images):
        image_enum_list.append((img.name, img.name, "", "", i))

    if len(image_enum_list) < 1:
        image_enum_list.append(('', '', "", "", 0))

    return image_enum_list


classes = (
    BN_OT_BakeBentNormals,
    BN_PT_Panel,
    BN_PT_CreatePanel,
    BN_Preferences
)


def register():
    from bpy.types import WindowManager
    from bpy.props import (
        StringProperty,
        EnumProperty,
        IntProperty,
        BoolProperty
    )

    WindowManager.ray_count = IntProperty(
        name="Ray Count",
        default=30,
        description="Number of rays for bent normal baking",
        min=2,
        max=1000
    )

    WindowManager.ray_length = IntProperty(
        name="Ray Length",
        default=60,
        description="Ray length used for bent normal baking",
        min=2,
        max=1000
    )

    WindowManager.mask_name = StringProperty(
        name="Mask name",
        default="bn_mask"
    )

    WindowManager.Normal = EnumProperty(
        items=enum_images_normal,
    )

    WindowManager.Height = EnumProperty(
        items=enum_images_height,
    )

    WindowManager.tiled = BoolProperty(
        name="Tiled",
        default=True,
        description="Specify whether the image should be tiled during bent normal calculations"
    )

    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    from bpy.types import WindowManager

    del WindowManager.ray_count
    del WindowManager.ray_length
    del WindowManager.mask_name
    del WindowManager.Normal
    del WindowManager.Height
    del WindowManager.tiled

    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
