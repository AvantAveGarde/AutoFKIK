import pymel.core as pm


def squash_stretch_ik(direction):
    driver = direction + "Leg_IK_Length.distance"
    thigh_length = pm.getAttr(direction + "Knee_IK_JNT.translateX")
    shin_length = pm.getAttr(direction + "Foot_IK_JNT.translateX")
    sum_length = thigh_length + shin_length
    if sum_length < 0:
        sum_length *= -1

    knee_joint = direction + "Knee_IK_JNT"
    foot_joint = direction + "Foot_IK_JNT"
    pm.setDrivenKeyframe(knee_joint, cd=driver, dv=sum_length, at="translateX", v=thigh_length)
    pm.setDrivenKeyframe(knee_joint, cd=driver, dv=sum_length * 2, at="translateX", v=thigh_length * 2)
    pm.setDrivenKeyframe(foot_joint, cd=driver, dv=sum_length, at="translateX", v=shin_length)
    pm.setDrivenKeyframe(foot_joint, cd=driver, dv=sum_length * 2, at="translateX", v=shin_length * 2)


def squash_stretch_fk(direction):
    thigh_joint = direction + "Thigh_FK_JNT"
    knee_joint = direction + "Knee_FK_JNT"
    foot_joint = direction + "Foot_FK_JNT"

    thigh_length = pm.getAttr(direction + "Knee_FK_JNT.translateX")
    shin_length = pm.getAttr(direction + "Foot_FK_JNT.translateX")
    pm.setDrivenKeyframe(knee_joint, cd=thigh_joint + ".Length", dv=0, at="translateX", v=0)
    pm.setDrivenKeyframe(foot_joint, cd=knee_joint + ".Length", dv=0, at="translateX", v=0)
    pm.setDrivenKeyframe(knee_joint, cd=thigh_joint + ".Length", dv=1, at="translateX", v=thigh_length)
    pm.setDrivenKeyframe(knee_joint, cd=thigh_joint + ".Length", dv=2, at="translateX", v=thigh_length * 2)
    pm.setDrivenKeyframe(foot_joint, cd=knee_joint + ".Length", dv=1, at="translateX", v=shin_length)
    pm.setDrivenKeyframe(foot_joint, cd=knee_joint + ".Length", dv=2, at="translateX", v=shin_length * 2)
    pass


if __name__ == "__main__":
    squash_stretch_ik("Left")
    squash_stretch_ik("Right")
    squash_stretch_fk("Left")
    squash_stretch_fk("Right")
