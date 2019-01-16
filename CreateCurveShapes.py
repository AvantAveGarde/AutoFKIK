import pymel.core as pm

'''
Be sure to delete compiled code, when running and making changes in Maya
'''
def color_controller(controller, color):
    # set override enabled
    # set color
    # yellow=17, 6=Blue, red=13
    controller.overrideEnabled.set(True)
    controller.getShape().overrideEnabled.set(True)

    color_switcher = {
        "Red": 13,
        "Blue": 6,
        "Yellow": 17
    }
    controller.overrideColor.set(color_switcher[color])
    controller.getShape().overrideColor.set(color_switcher[color])


'''
Shape name, the name of the curve shape, mapped to the dictionary which calls a function using the control name as
the name parameter and color.
'''
def create_shape_from_string(shape_name="", control_name="", color=0):
    function_switcher = {
        "Box": create_cube,
        "Circle": create_circle,
        "Four Arrows": create_4_arrows,
        "Turn Arrows": create_turn_arrows,
        "Wire Sphere": create_wire_sphere,
        "Diamond": create_diamond,
    }

    return function_switcher[shape_name](control_name, color)

def create_circle(name="", color=0):
    circle_crv = pm.circle(n=name)
    if color > 0:
        color_controller(circle_crv[0], color)
    return circle_crv[0]


def create_turn_arrows(name="", color=0):
    turn_arrows = pm.curve(n=name, d=1, p=[(0.613, 5.28, 0.0),
                                                          (-0.391, 4.58, 0.0),
                                                          (-1.27, 3.63, 0.0),
                                                          (-1.60, 3.09, 0.0),
                                                          (-1.884, 2.537, 0.0),
                                                          (-2.098, 1.957, 0.0),
                                                          (-2.25, 1.355, 0.0),
                                                          (-2.343, 0.731, 0.0),
                                                          (-2.374, 0.085, 0.0),
                                                          (-2.345, -0.557, 0.0),
                                                          (-2.258, -1.176, 0.0),
                                                          (-2.113, -1.771, 0.0),
                                                          (-1.909, -2.342, 0.0),
                                                          (-1.356, -3.381, 0.0),
                                                          (-0.716, -4.222, 0.0),
                                                          (0.365, -5.373, 0.0),
                                                          (-2.388, -6.428, 0.0),
                                                          (2.200, -6.219, 0.0),
                                                          (2.161, -2.519, 0.0),
                                                          (1.193, -4.573, 0.0),
                                                          (0.137, -3.459, 0.0),
                                                          (-0.321, -2.752, 0.0),
                                                          (-0.735, -1.852, 0.0),
                                                          (-0.898, -1.396, 0.0),
                                                          (-1.014, -0.921, 0.0),
                                                          (-1.084, -0.427, 0.0),
                                                          (-1.107, 0.0853, 0.0),
                                                          (-1.082, 0.601, 0.0),
                                                          (-1.007, 1.100, 0.0),
                                                          (-0.883, 1.582, 0.0),
                                                          (-0.709, 2.047, 0.0),
                                                          (-0.485, 2.496, 0.0),
                                                          (-0.211, 2.927, 0.0),
                                                          (0.450, 3.892, 0.0),
                                                          (1.118, 4.65, 0.0),
                                                          (2.273, 1.951, 0.0),
                                                          (2.388, 6.400, 0.0),
                                                          (-2.212, 6.428, 0), (.613, 5.29, 0)])
    pm.setAttr(turn_arrows.scale, .3, .3, .3, type="float3")
    pm.makeIdentity(apply=True, t=1, r=1, s=1, n=0)
    
    if color > 0:
        color_controller(turn_arrows, color)
    return turn_arrows


def create_cube(name="", color=0):
    cube_crv = pm.curve(n=name, d=1, p=[(1, 1, -1), (1, 1, 1), (1, -1, 1), (1, -1, -1), (1, 1, -1),
                                                (-1, 1, -1), (-1, 1, 1), (1, 1, 1), (1, -1, 1), (-1, -1, 1),
                                                (-1, 1, 1), (-1, -1, 1), (-1, -1, -1), (-1, 1, -1), (-1, -1, -1),
                                                (1, -1, -1)])  # d, degree; p, point;
    if color > 0:
        color_controller(cube_crv, color)
    return cube_crv


def create_4_arrows(name="", color=0):
    four_arrows = pm.curve(n=name, d=1, p=[(-.5, 0, -.5), (-.5, 0, -1.5),  (-1, 0, -1.5), (0, 0, -2.5),
                                                    (1, 0, -1.5),  (.5, 0, -1.5),   (.5, 0, -.5),  (1.5, 0, -.5),
                                                    (1.5, 0, -1),  (2.5, 0, 0),     (1.5, 0, 1),   (1.5, 0, .5),
                                                    (.5, 0, .5),   (.5, 0, 1.5),    (1, 0, 1.5),   (0, 0, 2.5),
                                                    (-1, 0, 1.5),  (-.5, 0, 1.5),   (-.5, 0, .5),  (-1.5, 0, .5),
                                                    (-1.5, 0, 1),  (-2.5, 0, 0),    (-1.5, 0, -1), (-1.5, 0, -.5),
                                                    (-.5, 0, -.5)])
    if color > 0:
        color_controller(four_arrows, color)
    return four_arrows

def create_diamond(name="", color=0):
    diamond = pm.curve(n=name, d=1, p=[(0.0, 0.0, 1.0),
                                       (-1.0, 0.0, 0.0),
                                       (0.0, 0.0, -1.0),
                                       (1.0, 0.0, 0.0),
                                       (0.0, 0.0, 1.0),
                                       (0.0, -1.0, 0.0),
                                       (-1.0, 0.0, 0.0),
                                       (0.0, -1.0, 0.0),
                                       (0.0, 0.0, -1.0),
                                       (0.0, -1.0, 0.0),
                                       (1.0, 0.0, 0.0),
                                       (0.0, 0.0, 1.0),
                                       (0.0, 1.0, 0.0),
                                       (-1.0, 0.0, 0.0),
                                       (0.0, 1.0, 0.0),
                                       (0.0, 0.0, -1.0),
                                       (0.0, 1.0, 0.0),
                                       (1.0, 0.0, 0.0)
                                       ])
    if color > 0:
        color_controller(diamond, color)
    return diamond

def create_wire_sphere(name="", color=0):
    wire_sphere = pm.circle(name=name, nr=(0, 0, 1))
    temp1 = pm.circle(name=name + '#', nr=(1, 0, 0))
    temp2 = pm.circle(name=name + '#', nr=(0, 1, 0))

    pm.parent(temp1[0] + "Shape", wire_sphere[0], s=True, r=True)
    pm.parent(temp2[0] + "Shape", wire_sphere[0], s=True, r=True)
    pm.delete(temp1)
    pm.delete(temp2)
    if color > 0:
        color_controller(wire_sphere[0], color)
    return wire_sphere[0]