import sys
import pybullet as p
import pybullet_data
from utils import resource_path

# Live-view: 640x480 keeps GPU readback at ~1.2 MB/frame vs 3.7 MB at 1280x720.
# The image is scaled to fit the widget anyway, so perceived quality is identical.
_LIVE_W = 640
_LIVE_H = 480

# High-quality resolution used exclusively when capturing PDF snapshots.
_SNAP_W = 1024
_SNAP_H = 768


class RobotSimulation:
    def __init__(self):
        p.connect(p.DIRECT)
        if hasattr(sys, '_MEIPASS'):
            p.setAdditionalSearchPath(resource_path('pybullet_data'))
        else:
            p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.81)
        p.createMultiBody(
            baseMass=0,
            baseCollisionShapeIndex=p.createCollisionShape(p.GEOM_PLANE),
            baseVisualShapeIndex=p.createVisualShape(
                p.GEOM_PLANE, rgbaColor=[0.95, 0.95, 0.95, 1]
            ),
        )
        try:
            self.robot = p.loadURDF(resource_path("PAROL6.urdf"), useFixedBase=True)
        except Exception:
            self.robot = p.loadURDF("kuka_iiwa/model.urdf", useFixedBase=True)

        self.joint_indices = [
            i
            for i in range(p.getNumJoints(self.robot))
            if p.getJointInfo(self.robot, i)[2] == p.JOINT_REVOLUTE
        ]
        self.joint_limits = [
            p.getJointInfo(self.robot, i)[8:10] for i in self.joint_indices
        ]

        # Camera position - robot center ~= z=0.28 for PAROL6.
        self._view_mat = p.computeViewMatrixFromYawPitchRoll(
            cameraTargetPosition=[0.0, 0.0, 0.28],
            distance=0.95,
            yaw=35,
            pitch=-22,
            roll=0,
            upAxisIndex=2,
        )
        # Pre-compute projection matrices for both resolutions.
        self._proj_live = p.computeProjectionMatrixFOV(
            fov=52, aspect=_LIVE_W / _LIVE_H, nearVal=0.05, farVal=5.0
        )
        self._proj_snap = p.computeProjectionMatrixFOV(
            fov=52, aspect=_SNAP_W / _SNAP_H, nearVal=0.05, farVal=5.0
        )

    # ------------------------------------------------------------------ #

    def get_joint_states(self):
        return [p.getJointState(self.robot, idx)[0] for idx in self.joint_indices]

    def set_joint_position(self, joint_idx, value):
        p.setJointMotorControl2(
            self.robot,
            self.joint_indices[joint_idx],
            p.POSITION_CONTROL,
            targetPosition=value,
            force=500,
            maxVelocity=8.0,
        )

    def set_joint_instant(self, joint_idx, value):
        """Teleport joint to value with zero velocity — for manual slider control."""
        idx = self.joint_indices[joint_idx]
        p.resetJointState(self.robot, idx, value, 0.0)
        # Hold the position so PyBullet's motor doesn't drift under gravity.
        p.setJointMotorControl2(
            self.robot, idx, p.POSITION_CONTROL,
            targetPosition=value, force=500, maxVelocity=8.0,
        )

    def get_camera_image(self):
        """1280x720 HD image for the live HMI view."""
        _, _, rgb, _, _ = p.getCameraImage(
            _LIVE_W, _LIVE_H,
            self._view_mat,
            self._proj_live,
            renderer=p.ER_TINY_RENDERER,
        )
        return rgb, _LIVE_W, _LIVE_H

    def get_snapshot_image(self):
        """1024x768 image for high-quality PDF snapshots."""
        _, _, rgb, _, _ = p.getCameraImage(
            _SNAP_W, _SNAP_H,
            self._view_mat,
            self._proj_snap,
            renderer=p.ER_TINY_RENDERER,
        )
        return rgb, _SNAP_W, _SNAP_H

    def step(self):
        # 2 sub-steps per tick — sufficient for position-controlled arm with no heavy contacts.
        p.stepSimulation()
        p.stepSimulation()
