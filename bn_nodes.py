# Copyright (C) 2022, Francis LaBounty, All rights reserved.

import bpy


def BN_CreateBentNormalGroup(name):
    """
    Creates a node group for using bent normals with a mask texture.

    Returns -> node group
    """
    # create normal group
    nodes = bpy.context.active_object.active_material.node_tree.nodes
    normal_group = nodes.new('ShaderNodeGroup')
    normal_group_tree = bpy.data.node_groups.new(name, 'ShaderNodeTree')

    # create group inputs
    group_inputs = normal_group_tree.nodes.new('NodeGroupInput')
    group_inputs.location = (-1000, 0)
    normal_group_tree.inputs.new('NodeSocketVectorXYZ', 'Mapping')
    normal_group_tree.inputs.new('NodeSocketFloat', 'Shadow Strength')
    normal_group_tree.inputs['Shadow Strength'].default_value = 1.0
    normal_group_tree.inputs.new('NodeSocketFloat', 'Normal Strength')
    normal_group_tree.inputs['Normal Strength'].default_value = 1.0

    # create group outputs
    group_output = normal_group_tree.nodes.new('NodeGroupOutput')
    group_output.location = (1350, 0)
    normal_group_tree.outputs.new('NodeSocketVectorXYZ', 'Bent Normal')

    # create internal group nodes
    # images
    node_image_mask = normal_group_tree.nodes.new('ShaderNodeTexImage')
    node_image_mask.name = "Mask"
    node_image_mask.location = (-750, 200)

    node_image_original_normal = normal_group_tree.nodes.new(
        'ShaderNodeTexImage')
    node_image_original_normal.name = "Original Normal"
    node_image_original_normal.location = (-750, -200)

    # separate rgb
    node_separateRGB_mask = normal_group_tree.nodes.new(
        'ShaderNodeSeparateRGB')
    node_separateRGB_mask.name = "Mask Separate RGB"
    node_separateRGB_mask.location = (-400, 200)

    node_separateRGB_original_normal = normal_group_tree.nodes.new(
        'ShaderNodeSeparateRGB')
    node_separateRGB_original_normal.name = "Original Normal Separate RGB"
    node_separateRGB_original_normal.location = (-400, -200)

    # map range
    node_mapping_mask_red = normal_group_tree.nodes.new('ShaderNodeMapRange')
    node_mapping_mask_red.name = "Mask Red Map Range"
    node_mapping_mask_red.clamp = False
    node_mapping_mask_red.inputs[3].default_value = -1.0
    node_mapping_mask_red.location = (-150, 500)

    node_mapping_mask_green = normal_group_tree.nodes.new('ShaderNodeMapRange')
    node_mapping_mask_green.name = "Mask Green Map Range"
    node_mapping_mask_green.clamp = False
    node_mapping_mask_green.inputs[3].default_value = -1.0
    node_mapping_mask_green.location = (-150, 200)

    node_mapping_original_normal_red = normal_group_tree.nodes.new(
        'ShaderNodeMapRange')
    node_mapping_original_normal_red.name = "Original Normal Red Map Range"
    node_mapping_original_normal_red.clamp = False
    node_mapping_original_normal_red.inputs[3].default_value = -1.0
    node_mapping_original_normal_red.location = (-150, -200)

    node_mapping_original_normal_green = normal_group_tree.nodes.new(
        'ShaderNodeMapRange')
    node_mapping_original_normal_green.name = "Original Normal Green Map Range"
    node_mapping_original_normal_green.clamp = False
    node_mapping_original_normal_green.inputs[3].default_value = -1.0
    node_mapping_original_normal_green.location = (-150, -500)

    node_mapping_final_red = normal_group_tree.nodes.new('ShaderNodeMapRange')
    node_mapping_final_red.name = "Final Red Map Range"
    node_mapping_final_red.clamp = True
    node_mapping_final_red.inputs[1].default_value = -1.0
    node_mapping_final_red.location = (600, 200)

    node_mapping_final_green = normal_group_tree.nodes.new(
        'ShaderNodeMapRange')
    node_mapping_final_green.name = "Final Green Map Range"
    node_mapping_final_green.clamp = True
    node_mapping_final_green.inputs[1].default_value = -1.0
    node_mapping_final_green.location = (600, -200)

    # math nodes
    node_multiply_mask_red = normal_group_tree.nodes.new('ShaderNodeMath')
    node_multiply_mask_red.operation = "MULTIPLY"
    node_multiply_mask_red.name = "Mask Red Scale"
    node_multiply_mask_red.location = (100, 200)

    node_multiply_mask_green = normal_group_tree.nodes.new('ShaderNodeMath')
    node_multiply_mask_green.operation = "MULTIPLY"
    node_multiply_mask_green.name = "Mask Green Scale"
    node_multiply_mask_green.location = (100, -200)

    node_subtract_red = normal_group_tree.nodes.new('ShaderNodeMath')
    node_subtract_red.operation = "SUBTRACT"
    node_subtract_red.name = "Subtract Red"
    node_subtract_red.location = (350, 200)

    node_subtract_green = normal_group_tree.nodes.new('ShaderNodeMath')
    node_subtract_green.operation = "SUBTRACT"
    node_subtract_green.name = "Subtract Green"
    node_subtract_green.location = (350, -200)

    # combine rgb
    node_combineRGB = normal_group_tree.nodes.new('ShaderNodeCombineRGB')
    node_combineRGB.name = "Combine RGB"
    node_combineRGB.location = (850, 0)

    # normal map
    node_final_normal = normal_group_tree.nodes.new('ShaderNodeNormalMap')
    node_final_normal.name = "Final Normal"
    node_final_normal.location = (1100, 0)

    # link inputs
    normal_group_tree.links.new(
        group_inputs.outputs['Mapping'], node_image_mask.inputs[0])
    normal_group_tree.links.new(
        group_inputs.outputs['Mapping'], node_image_original_normal.inputs[0])

    normal_group_tree.links.new(
        group_inputs.outputs['Shadow Strength'], node_multiply_mask_red.inputs[1])
    normal_group_tree.links.new(
        group_inputs.outputs['Shadow Strength'], node_multiply_mask_green.inputs[1])

    normal_group_tree.links.new(
        group_inputs.outputs['Normal Strength'], node_final_normal.inputs[0])

    # link internals
    normal_group_tree.links.new(
        node_image_mask.outputs[0], node_separateRGB_mask.inputs[0])
    normal_group_tree.links.new(
        node_separateRGB_mask.outputs[0], node_mapping_mask_red.inputs[0])
    normal_group_tree.links.new(
        node_separateRGB_mask.outputs[1], node_mapping_mask_green.inputs[0])
    normal_group_tree.links.new(
        node_mapping_mask_red.outputs[0], node_multiply_mask_red.inputs[0])
    normal_group_tree.links.new(
        node_mapping_mask_green.outputs[0], node_multiply_mask_green.inputs[0])

    normal_group_tree.links.new(
        node_image_original_normal.outputs[0], node_separateRGB_original_normal.inputs[0])
    normal_group_tree.links.new(
        node_separateRGB_original_normal.outputs[0], node_mapping_original_normal_red.inputs[0])
    normal_group_tree.links.new(
        node_separateRGB_original_normal.outputs[1], node_mapping_original_normal_green.inputs[0])

    normal_group_tree.links.new(
        node_multiply_mask_red.outputs[0], node_subtract_red.inputs[1])
    normal_group_tree.links.new(
        node_multiply_mask_green.outputs[0], node_subtract_green.inputs[1])
    normal_group_tree.links.new(
        node_mapping_original_normal_red.outputs[0], node_subtract_red.inputs[0])
    normal_group_tree.links.new(
        node_mapping_original_normal_green.outputs[0], node_subtract_green.inputs[0])

    normal_group_tree.links.new(
        node_subtract_red.outputs[0], node_mapping_final_red.inputs[0])
    normal_group_tree.links.new(
        node_subtract_green.outputs[0], node_mapping_final_green.inputs[0])

    normal_group_tree.links.new(
        node_mapping_final_red.outputs[0], node_combineRGB.inputs[0])
    normal_group_tree.links.new(
        node_mapping_final_green.outputs[0], node_combineRGB.inputs[1])
    normal_group_tree.links.new(
        node_separateRGB_original_normal.outputs[2], node_combineRGB.inputs[2])

    normal_group_tree.links.new(
        node_combineRGB.outputs[0], node_final_normal.inputs[1])

    # link output
    normal_group_tree.links.new(
        node_final_normal.outputs[0], group_output.inputs['Bent Normal'])
    normal_group.node_tree = normal_group_tree
    normal_group.location = (-300, -100)
    return normal_group


# search for a node by name
def BN_NodeSearch(group, name):
    for node in group.nodes:
        if name in node.name:
            return node
    return None
