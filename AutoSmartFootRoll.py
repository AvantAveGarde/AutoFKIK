import pymel.core as pm

'''
Auto Smart Foot Roll - Written by Colton Lee
Before running this script, create three locators and place them at the
appropriate spots.

1) Heel Loc - Located at the base of the foot
2) Ball Loc - Located at the ball joint
3) Toe Loc - Located at the toe end joint

Afterwards in the outliner change the hierarchy of your IK Handles and 
Locators as follows.
4) Parent both the toe loc and toe IK Handle under the heel loc
5) Parent the ball loc under the toe loc
6) Parent the Leg IK Handle and the and the Ball IK Handle under the ball loc

7) Change the direction variable as desired and run the script
'''


def main():
    direction = "Left"
    foot_ctrl = direction + "Leg_IK_CTRL"
    heel_loc = direction + "Heel_LOC"
    ball_loc = direction + "Ball_LOC"
    toe_loc = direction + "Toe_LOC"

    # Adds the appropriate attributes to the IK Controller
    pm.addAttr(foot_ctrl, ln="FootRoll", at="double", dv=0, k=True)
    pm.addAttr(foot_ctrl, ln="BendLimitAngle", at="double", dv=45, k=True)
    pm.addAttr(foot_ctrl, ln="BendStraightAngle", at="double", dv=70, k=True)

    # Makes the heel rotate only with a negative value
    heel_clamp = pm.shadingNode('clamp', au=True, n=direction + "Heel_RotClamp")
    pm.setAttr(heel_clamp + ".minR", -90)
    pm.connectAttr(foot_ctrl + ".FootRoll", heel_clamp + ".inputR")
    pm.connectAttr(heel_clamp + ".outputR", heel_loc + ".rotateX")

    # Makes the ball rotate only with a forward value
    ball_ztb_clamp = pm.shadingNode('clamp', au=True, n=direction + "Ball_ZeroToBend_Clamp")
    pm.connectAttr(foot_ctrl + ".BendLimitAngle", ball_ztb_clamp + ".maxR")
    pm.connectAttr(foot_ctrl + ".FootRoll", ball_ztb_clamp + ".inputR")

    ball_ztb_pcrt = pm.shadingNode("setRange", au=True, n=direction + "Foot_BendToStraight_Percent")
    pm.connectAttr(ball_ztb_clamp + ".minR", ball_ztb_pcrt + ".oldMinX")
    pm.connectAttr(ball_ztb_clamp + ".maxR", ball_ztb_pcrt + ".oldMaxX")
    pm.setAttr(ball_ztb_pcrt + ".minX", 0)
    pm.setAttr(ball_ztb_pcrt + ".maxX", 1)
    pm.connectAttr(ball_ztb_clamp + ".inputR", ball_ztb_pcrt + ".valueX")

    # Makes the toe rotate when the bend limit angle is hit and rotates until the toe straight angle is reached
    foot_bts_clamp = pm.shadingNode('clamp', au=True, n=direction + "Foot_BendToStraight_Clamp")
    pm.connectAttr(foot_ctrl + ".BendLimitAngle", foot_bts_clamp + ".minR")
    pm.connectAttr(foot_ctrl + ".BendStraightAngle", foot_bts_clamp + ".maxR")
    pm.connectAttr(foot_ctrl + ".FootRoll", foot_bts_clamp + ".inputR")
    foot_bts_pcrt = pm.shadingNode("setRange", au=True, n=direction + "Foot_BendToStraight_Percent")
    pm.connectAttr(foot_bts_clamp + ".minR", foot_bts_pcrt + ".oldMinX")
    pm.connectAttr(foot_bts_clamp + ".maxR", foot_bts_pcrt + ".oldMaxX")
    pm.setAttr(foot_bts_pcrt + ".maxX", 1)
    pm.connectAttr(foot_bts_clamp + ".inputR", foot_bts_pcrt + ".valueX")
    foot_roll_mult = pm.shadingNode("multiplyDivide", au=True, n=direction + "Foot_Roll_MULT")
    pm.connectAttr(foot_bts_pcrt + ".outValueX", foot_roll_mult + ".input1X")
    pm.connectAttr(foot_bts_clamp + ".inputR", foot_roll_mult + ".input2X")
    pm.connectAttr(foot_roll_mult + ".outputX", toe_loc + ".rotateX")

    foot_invert_pcrt = pm.shadingNode("plusMinusAverage", au=True, n=direction + "Foot_InvertPercentage")
    pm.setAttr(foot_invert_pcrt + ".input1D[0]", 1)
    pm.setAttr(foot_invert_pcrt + ".input1D[1]", 1)
    pm.connectAttr(foot_bts_pcrt + ".outValueX", foot_invert_pcrt + ".input1D[1]")
    pm.setAttr(foot_invert_pcrt + ".operation", 2)
    ball_pcrt_mult = pm.shadingNode("multiplyDivide", au=True, n=direction + "Foot_Percent_MULT")
    pm.connectAttr(ball_ztb_pcrt + ".outValueX", ball_pcrt_mult + ".input1X")
    pm.connectAttr(foot_invert_pcrt + ".output1D", ball_pcrt_mult + ".input2X")
    ball_roll_mult = pm.shadingNode("multiplyDivide", au=True, n=direction + "Foot_Roll_MULT")
    pm.connectAttr(ball_pcrt_mult + ".outputX", ball_roll_mult + ".input1X")
    pm.connectAttr(foot_ctrl + ".FootRoll", ball_roll_mult + ".input2X")
    pm.connectAttr(ball_roll_mult + ".outputX", ball_loc + ".rotateX")


if __name__ == "__main__":
    main()