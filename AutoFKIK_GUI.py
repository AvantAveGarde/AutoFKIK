import pymel.core as pm

script_name = __name__
new_window = "AutoFKIK"


def gui():
    if pm.window(new_window, q=True, exists=True):
        pm.deleteUI(new_window)
    if pm.windowPref(new_window, q=True, exists=True):
        pm.windowPref(new_window, r=True)
    main_window = pm.window(new_window, t='Auto Arm Rig', w=200, h=250)
    main_layout = pm.frameLayout("Main Header")
    column_layout = pm.columnLayout()
    pm.text("naming_setup_label", l="Step 1: Naming Setup ")
    pm.rowLayout(numberOfColumns=2)
    pm.text("appendage_name_label", l="Appendage Name: ")
    pm.textField("appendage_name_input")
    pm.setParent("..")
    pm.rowLayout(numberOfColumns=2)
    pm.text("z_direction_offset_label", l="Z Direction Offset: ")
    z_direction_offset = pm.textField("z_direction_offset_input")
    pm.setParent("..")
    pm.button("ok_button", l="OK", w=250, command=on_ok_pressed)
    pm.showWindow()

def on_ok_pressed(*args):
    print(pm.textField("z_direction_offset_input", q=True, text=True))
    print("hello")
    
def test():
    pass


gui()
#test()