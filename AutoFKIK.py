# Written by Colton "AvantAveGarde" Lee
# For any issues mail to coltonyenlee@outlook.com

import pymel.core as pm
import CreateCurveShapes

script_name = __name__
new_window = "AutoFKIK"

def get_name_prefixes(i_selected_items):
    prefix_list = []
    for item in i_selected_items:
        count = 0
        underscore_found = False
        item_prefix = ""
        while not underscore_found and count < len(str(item)):
            if item[count] == "_":
                underscore_found = True
            else:
                item_prefix += item[count]
                count += 1
        prefix_list.append(item_prefix)
    return prefix_list

'''
Duplicates the incoming result joint chain, renames them, parents shape curves to them and returns the fk joint chain
fk_joints = attach_fk_to_joints(result_joints, fk_icon, fk_color, fk_scale_list)
'''
def attach_fk_to_joints(i_joints, i_fk_icon, i_fk_color, i_fk_scale_list):

    # duplicate and rename
    fk_joints = pm.duplicate(i_joints, po=True)
    pm.rename(fk_joints[0], fk_joints[0][:-12] + "_FK_JNT")
    for joint in fk_joints[1::]:
        pm.rename(joint, joint[:-11] + "_FK_JNT")

    # create curves and parent
    for i in range(len(fk_joints) - 1):
        fk_curve = CreateCurveShapes.create_shape_from_string(i_fk_icon, fk_joints[i][:-3] + "CRV", i_fk_color)
        pm.setAttr(fk_curve.scale, i_fk_scale_list[i])
        pm.makeIdentity(fk_curve, apply=True, t=1, r=1, s=1, n=0)
        pm.parent(fk_curve + "Shape", fk_joints[i], r=True, s=True)
        pm.delete(fk_curve)
    return fk_joints


'''
Duplicates the incoming result joint chain, renames them, creates an ikHandle that is parented to a cube curve
and returns the ik joint chain.
attach_ik_to_joints(result_joints, appendage_name, name_prefixes[1], ik_icon, pv_icon, ik_color, pv_pos)
'''
def attach_ik_to_joints(i_joints, handle_name, pv_name, i_ik_icon, i_pv_icon, i_ik_color,
                        i_pv_pos, i_ik_icon_scale, i_pv_icon_scale):
    # duplicates result joint chain to create ik joints
    ik_joints = pm.duplicate(i_joints, po=True)
    pm.rename(ik_joints[0], ik_joints[0][:-12] + "_IK_JNT")
    for joint in ik_joints[1::]:
        pm.rename(joint, joint[:-11] + "_IK_JNT")

    # create IK HDL and Curve
    ik_handle = pm.ikHandle(sj = ik_joints[0], ee = ik_joints[2], n=handle_name + "_HDL")
    pm.rename("effector1", handle_name + "_EFF")
    ik_handle_control = CreateCurveShapes.create_shape_from_string(i_ik_icon, handle_name + "_IK_CTRL", i_ik_color)
    pm.setAttr(ik_handle_control.scale, i_ik_icon_scale)
    pm.makeIdentity(ik_handle_control, apply=True, t=1, r=1, s=1, n=0)
    handle_pos = pm.xform(i_joints[-1], query=True, worldSpace=True, translation=True)
    pm.xform(ik_handle_control, worldSpace=True, translation=handle_pos)
    pm.parent(ik_handle[0], ik_handle_control)

    # create Ankle Handles and parent to curve
    ankle_ik_handle = pm.ikHandle(sj=ik_joints[2], ee=ik_joints[3], n=handle_name + "Ankle_HDL")
    pm.rename("effector1", handle_name + "_Ankle_EFF")
    pm.parent(ankle_ik_handle[0], ik_handle_control)

    # Create Toe IK Handles and Parent to curve
    toe_ik_handle = pm.ikHandle(sj=ik_joints[3], ee=ik_joints[4], n=handle_name + "Toe_HDL")
    pm.rename("effector1", handle_name + "_EFF")
    pm.parent(toe_ik_handle[0], ik_handle_control)


    # create knee pole vector constraint
    pv_control = CreateCurveShapes.create_shape_from_string(i_pv_icon, pv_name + "_CTRL", i_ik_color)
    pm.setAttr(pv_control.scale, i_pv_icon_scale)
    pm.xform(pv_control, worldSpace=True, translation=i_pv_pos)
    pm.makeIdentity(pv_control, apply=True, t=1, r=1, s=1, n=0)
    pm.poleVectorConstraint(pv_control, ik_handle[0])
    return ik_joints


'''
Creates blend color nodes for the fk/ik joint chains, and connects their outputs to the result joint chain.
'''
def attach_fk_ik_to_blend_to_result(i_fk_joints, i_ik_joints, i_result_joints, i_name_prefixes):
    blend_nodes = []
    if len(i_fk_joints) == len(i_ik_joints) and len(i_ik_joints) == len(i_result_joints):
        for i in range(len(i_fk_joints)):
            translation_blend = pm.shadingNode('blendColors', au=True, n=i_name_prefixes[i] + "Trans_FKIK_Blend")
            rotation_blend = pm.shadingNode('blendColors', au=True, n=i_name_prefixes[i] + "Rot_FKIK_Blend")
            pm.connectAttr(i_ik_joints[i].translate, translation_blend.color1)
            pm.connectAttr(i_ik_joints[i].rotate, rotation_blend.color1)

            pm.connectAttr(i_fk_joints[i].translate, translation_blend.color2)
            pm.connectAttr(i_fk_joints[i].rotate, rotation_blend.color2)

            pm.connectAttr(translation_blend.output, i_result_joints[i].translate)
            pm.connectAttr(rotation_blend.output, i_result_joints[i].rotate)
            blend_nodes.append(translation_blend) ; blend_nodes.append(rotation_blend)
    else:
        print("Mismatching FK/IK/Result Chain Joint Size")
    return blend_nodes

'''
Creates the settings control that manages the FK/IK blend attribute as well as the FK/IK Visibility.
'''
def create_fk_ik_settings_control(i_appendage_name, i_pv_name, i_result_joints, i_connection_list, i_fk_joints, i_settings_icon,
                                  i_settings_color, i_settings_pos, i_settings_icon_scale):
    # Creating the settings control curve, and setting it's position based on the last joint in the
    # result joint chain with an offset of 6
    settings_control = CreateCurveShapes.create_shape_from_string(i_settings_icon,
                                                                  i_appendage_name + "_Settings_CTRL", i_settings_color)
    pm.setAttr(settings_control.scale, i_settings_icon_scale)
    pm.xform(settings_control, worldSpace=True, translation=i_settings_pos)
    pm.makeIdentity(settings_control, apply=True, t=1, r=1, s=1, n=0)
    pm.parentConstraint(i_result_joints[-1], settings_control, mo=True)

    # Adding the individual attributes to the control and connecting them
    pm.addAttr(longName='FKIK_Blend', attributeType='float', min=0, max=1, keyable=True)
    pm.addAttr(longName='FK_Visibility', attributeType='bool', keyable=True)
    pm.addAttr(longName='IK_Visibility', attributeType='bool', keyable=True)
    for connection in i_connection_list:
        pm.connectAttr(settings_control + ".FKIK_Blend", connection + ".blender")
    ik_control = i_appendage_name + "_IK_CTRL"
    pm.connectAttr(settings_control + ".IK_Visibility", ik_control + ".visibility")
    for fk_joint in i_fk_joints:
        pm.connectAttr(settings_control + ".FK_Visibility", fk_joint + ".visibility")
    pm.connectAttr(settings_control + ".IK_Visibility", i_pv_name + "_CTRL" + ".visibility")

    # region REGION Setting individual driven keys based on the blend attribute and the IK/FK visibility.
    pm.setAttr(settings_control + ".FKIK_Blend", 0)
    pm.setAttr(settings_control + ".FK_Visibility", 1)
    pm.setAttr(settings_control + ".IK_Visibility", 0)
    pm.setDrivenKeyframe(settings_control + ".FK_Visibility", cd=settings_control + ".FKIK_Blend")
    pm.setDrivenKeyframe(settings_control + ".IK_Visibility", cd=settings_control + ".FKIK_Blend")
    pm.setAttr(settings_control + ".FKIK_Blend", 1)
    pm.setAttr(settings_control + ".FK_Visibility", 0)
    pm.setAttr(settings_control + ".IK_Visibility", 1)
    pm.setDrivenKeyframe(settings_control + ".FK_Visibility", cd=settings_control + ".FKIK_Blend")
    pm.setDrivenKeyframe(settings_control + ".IK_Visibility", cd=settings_control + ".FKIK_Blend")
    pm.setAttr(settings_control + ".FKIK_Blend", .001)
    pm.setAttr(settings_control + ".FK_Visibility", 1)
    pm.setAttr(settings_control + ".IK_Visibility", 1)
    pm.setDrivenKeyframe(settings_control + ".FK_Visibility", cd=settings_control + ".FKIK_Blend")
    pm.setDrivenKeyframe(settings_control + ".IK_Visibility", cd=settings_control + ".FKIK_Blend")
    pm.setAttr(settings_control + ".FKIK_Blend", .999)
    pm.setAttr(settings_control + ".FK_Visibility", 1)
    pm.setAttr(settings_control + ".IK_Visibility", 1)
    pm.setDrivenKeyframe(settings_control + ".FK_Visibility", cd=settings_control + ".FKIK_Blend")
    pm.setDrivenKeyframe(settings_control + ".IK_Visibility", cd=settings_control + ".FKIK_Blend")
    pm.setAttr(settings_control + ".FKIK_Blend", 1)
    # endregion

    return settings_control

'''
Cleans the outliner hiearchy by parenting the joint chains to respective motion system groups and result constant groups
'''
def parent_joints_to_groups(i_appendage_name, i_name_prefixes, i_result_joints, i_fk_joints, i_ik_joints, i_settings_control):
    motion_system_group = i_appendage_name + "Motion_SYS"
    result_constant_group = i_appendage_name + "Result_GRP"
    if not pm.objExists("Settings_GRP"):
        pm.group(i_settings_control, n='Settings_GRP')
    if not pm.objExists(result_constant_group):
        pm.group(em=True, name=result_constant_group)
        pm.group(em=True, name=motion_system_group)

    pm.parent(i_settings_control, "Settings_GRP")
    pm.parent(i_fk_joints[0], motion_system_group)
    pm.parent(i_ik_joints[0], motion_system_group)
    pm.parent(i_result_joints[0], result_constant_group)
    pm.parent(i_appendage_name + "_IK_CTRL", motion_system_group)
    pm.parent(i_name_prefixes[1] + "_CTRL", motion_system_group)

    lock_trans_scale_rot_vis(motion_system_group)
    lock_trans_scale_rot_vis(result_constant_group)
    lock_trans_scale_rot_vis("Settings_GRP")

'''
Locks the translation, scale, rotation and visibility channels.
'''
def lock_trans_scale_rot_vis(i_group):
    pm.setAttr(i_group + ".tx", lock=True, keyable=False, channelBox=False)
    pm.setAttr(i_group + ".ty", lock=True, keyable=False, channelBox=False)
    pm.setAttr(i_group + ".tz", lock=True, keyable=False, channelBox=False)
    pm.setAttr(i_group + ".rx", lock=True, keyable=False, channelBox=False)
    pm.setAttr(i_group + ".ry", lock=True, keyable=False, channelBox=False)
    pm.setAttr(i_group + ".rz", lock=True, keyable=False, channelBox=False)
    pm.setAttr(i_group + ".sx", lock=True, keyable=False, channelBox=False)
    pm.setAttr(i_group + ".sy", lock=True, keyable=False, channelBox=False)
    pm.setAttr(i_group + ".sz", lock=True, keyable=False, channelBox=False)
    pm.setAttr(i_group +  ".v", lock=True, keyable=False, channelBox=False)


'''
Main graphical interface
'''
def gui():
    if pm.window(new_window, q=True, exists=True):
        pm.deleteUI(new_window)
    if pm.windowPref(new_window, q=True, exists=True):
        pm.windowPref(new_window, r=True)
    main_window = pm.window(new_window, t='Auto Arm Rig', w=200, h=250)
    main_layout = pm.frameLayout("Auto FKIK Arm Tool")
    column_layout = pm.columnLayout()
    
    # Naming Setup Options
    pm.text("naming_setup_label", l="Step 1: Naming Setup ")
    pm.rowColumnLayout(numberOfColumns=3, cs=[(3,10)])
    pm.text("appendage_name_label", l="Appendage Name: ")
    pm.textField("appendage_name_input")
    pm.button("appendage_name_info_button", l="?", w=20, command="open_appendage_name_info")
    pm.setParent("..")
    pm.separator("naming_setup_separator", w=250, h=5)
    
    # Control Options
    pm.text("control_setup_label", l="Step 2: Pick Control Icons: ")
    pm.rowColumnLayout(numberOfColumns=2,cw=[(2,100)], cs=[(2, 20)])
    
    pm.text("fk_icon_setup_label", l="FK Icon: ")
    pm.optionMenu("fk_icon_menu")
    pm.menuItem(label="Circle")
    pm.menuItem(label="Turn Arrows")
    
    pm.text("ik_icon_setup_label", l="IK Icon: ")
    pm.optionMenu("ik_icon_menu")
    pm.menuItem(label="Box")
    pm.menuItem(label="Four Arrows")
    
    pm.text("pv_icon_setup_label", l="PV Icon: ")
    pm.optionMenu("pv_icon_menu")
    pm.menuItem(label="Wire Sphere")
    pm.menuItem(label="Diamond")
    
    pm.text("settings_icon_setup_label", l="Settings Icon: ")
    pm.optionMenu("settings_icon_menu")
    pm.menuItem(label="Box")
    pm.menuItem(label="Diamond")
    
    pm.setParent("..")
    
    pm.separator("control_setup_separator", w=250, h=5)
    
    # Color Options
    pm.text("color_setup_label", l="Step 3: Pick Icon Colors: ")
    pm.rowColumnLayout(numberOfColumns=2, cw=[(2,110)], cs=[(2, 13)])
    
    pm.text("fk_color_setup_label", l="FK Color: ")
    pm.optionMenu("fk_color_menu")
    pm.menuItem(label="Blue")
    pm.menuItem(label="Red")
    pm.menuItem(label="Yellow")
    
    pm.text("ik_color_setup_label", l="IK Color: ")
    pm.optionMenu("ik_color_menu")
    pm.menuItem(label="Blue")
    pm.menuItem(label="Red")
    pm.menuItem(label="Yellow")
    
    pm.text("settings_color_setup_label", l="Settings Color: ")
    pm.optionMenu("settings_color_menu")
    pm.menuItem(label="Blue")
    pm.menuItem(label="Red")
    pm.menuItem(label="Yellow")    
    
    pm.setParent("..")
    pm.button("test_icons_button", l="Make Test Icons and Set Scale", w=250, command="make_test_icons()")
    
    pm.text("advanced_options_label", l="Step 4: Advanced Options: (WIP)")
    pm.rowColumnLayout(numberOfColumns=3, cw=[(1,130)], cs=[(2, 13)])
    # TODO Squash Stretch
    pm.text("squash_stretch_label", l="Enable Squash/Stretch: ")
    pm.radioCollection("squash_stretch_radio_collection")
    pm.radioButton(label="On", en=False)
    pm.radioButton(label="Off", en=False)
    # TODO Twist Options
    pm.text("advanced_twist_label", l="Enable Advanced Twist: ")
    pm.radioCollection("advanced_twist_radio_collection")
    pm.radioButton(label="On", en=False)
    pm.radioButton(label="Off", en=False)
    
    pm.setParent("..")
    pm.button("finalize_button", l="Finalize and Make Arm", w=250, command="create_ik_fk_arm()")
    pm.showWindow()


'''
Makes the test icons so that the user may set the position, scale and rotation 
that is appropriate.
'''
def make_test_icons():
    result_joints = pm.ls(sl=True)
    if pm.objExists("Test_Icons_DO_NOT_DELETE_GRP"):
        pm.delete("Test_Icons_DO_NOT_DELETE_GRP")
    
    pm.group(em=True, n="Test_Icons_DO_NOT_DELETE_GRP")
    pm.group(em=True, n="FK_Icons_DO_NOT_DELETE_GRP", p="Test_Icons_DO_NOT_DELETE_GRP")
    pm.group(em=True, n="IK_Icons_DO_NOT_DELETE_GRP", p="Test_Icons_DO_NOT_DELETE_GRP")
    pm.group(em=True, n="Settings_Icons_DO_NOT_DELETE_GRP", p="Test_Icons_DO_NOT_DELETE_GRP")
    
    fk_icon = pm.optionMenu("fk_icon_menu", query=True, value=True)
    ik_icon = pm.optionMenu("ik_icon_menu", query=True, value=True)
    pv_icon = pm.optionMenu("pv_icon_menu", query=True, value=True)
    settings_icon = pm.optionMenu("settings_icon_menu", query=True, value=True)
    ik_color = pm.optionMenu("ik_color_menu", query=True, value=True)
    fk_color = pm.optionMenu("fk_color_menu", query=True, value=True)
    settings_color = pm.optionMenu("settings_color_menu", query=True, value=True)
    

    for joint in result_joints:
        circle = CreateCurveShapes.create_shape_from_string(fk_icon, joint[:-10] + "Test_CRV", fk_color)
        
        joint_rot = pm.xform(joint, query=True, worldSpace=True, rotation=True)
        joint_pos = pm.xform(joint, query=True, worldSpace=True, translation=True)
        
        pm.xform(circle, rotation=joint_rot)
        pm.xform(circle, worldSpace=True, translation=joint_pos)
        pm.parent(circle, "FK_Icons_DO_NOT_DELETE_GRP")
    
    ik_curve = CreateCurveShapes.create_shape_from_string(ik_icon, "IK_Test_CRV", ik_color)
    ik_pos = pm.xform(result_joints[-1], query=True, worldSpace=True, translation=True)
    pm.xform(ik_curve, worldSpace=True, translation=ik_pos)
    pv_curve = CreateCurveShapes.create_shape_from_string(pv_icon, "PV_Test_CRV", ik_color)
    pv_pos = pm.xform(result_joints[1], query=True, worldSpace=True, translation=True)
    pm.xform(pv_curve, worldSpace=True, translation=pv_pos)

    pm.parent(ik_curve, "IK_Icons_DO_NOT_DELETE_GRP")
    pm.parent(pv_curve, "IK_Icons_DO_NOT_DELETE_GRP")
    
    settings_curve = CreateCurveShapes.create_shape_from_string(settings_icon, "Settings_Test_CRV", settings_color)
    pm.xform(settings_curve, worldSpace=True, translation=ik_pos)
    pm.setAttr(settings_curve.scale, .5, .5, .5, type="float3")
    pm.parent(settings_curve, "Settings_Icons_DO_NOT_DELETE_GRP")
    
'''
Main functionality, acts as the controller that links the GUI and the defined functions
'''
def create_ik_fk_arm():
    result_joints = pm.ls(sl=True)
    appendage_name = pm.textField("appendage_name_input", q=True, text=True)
    name_prefixes = get_name_prefixes(result_joints)

    # Create FK Joints and Controls
    fk_icon = pm.optionMenu("fk_icon_menu", query=True, value=True)
    fk_color = pm.optionMenu("fk_color_menu", query=True, value=True)
    fk_scale_list = []
    for fk_curve in pm.listRelatives("FK_Icons_DO_NOT_DELETE_GRP"):
        fk_scale_list.append(pm.xform(fk_curve, query=True, worldSpace=True, scale=True))
    fk_joints = attach_fk_to_joints(result_joints, fk_icon, fk_color, fk_scale_list)

    # Create IK Joints and Controls
    ik_icon = pm.optionMenu("ik_icon_menu", query=True, value=True)
    ik_color = pm.optionMenu("ik_color_menu", query=True, value=True)
    ik_icon_scale = pm.xform("IK_Test_CRV", query=True, worldSpace=True, scale=True)
    pv_icon = pm.optionMenu("pv_icon_menu", query=True, value=True)
    pv_pos = pm.xform("PV_Test_CRV", query=True, worldSpace=True, translation=True)
    pv_icon_scale = pm.xform("PV_Test_CRV", query=True, worldSpace=True, scale=True)
    ik_joints = attach_ik_to_joints(result_joints, appendage_name, name_prefixes[1], ik_icon, pv_icon, ik_color, pv_pos,
                                    ik_icon_scale, pv_icon_scale)

    blend_nodes = attach_fk_ik_to_blend_to_result(fk_joints, ik_joints, result_joints, name_prefixes)
    settings_icon = pm.optionMenu("settings_icon_menu", query=True, value=True)
    settings_color = pm.optionMenu("settings_color_menu", query=True, value=True)
    settings_pos = pm.xform("Settings_Test_CRV", query=True, worldSpace=True, translation=True)
    settings_icon_scale = pm.xform("Settings_Test_CRV", query=True, worldSpace=True, scale=True)
    settings_control = create_fk_ik_settings_control(appendage_name, name_prefixes[1], result_joints, blend_nodes,
                                                     fk_joints, settings_icon, settings_color, settings_pos,
                                                     settings_icon_scale)

    parent_joints_to_groups(appendage_name, name_prefixes, result_joints, fk_joints, ik_joints, settings_control)
    
    pm.delete("Test_Icons_DO_NOT_DELETE_GRP")
    pm.deleteUI(new_window)
def test():
    turn_arrow = CreateCurveShapes.create_turn_arrows("test", "Blue")
    circle = pm.circle(name="hello")
    print(circle.shortName())
    pass

gui()
#test()