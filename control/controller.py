import numpy as np

MODE_MANUAL = 0
MODE_AUTO_PDF = 6
MODE_AUTO_HOME = 7


class RobotController:
    SPEED = 1.0
    # 0.14 rad/tick × 50 FPS = 7.0 rad/s cruise. Matches PyBullet maxVelocity=8.0.
    MAX_STEP = 0.14
    ARRIVAL_THRESHOLD = 0.02

    def __init__(self, simulation):
        self.sim = simulation
        self.auto_mode = MODE_MANUAL
        self.target_joint_dest = None

    def set_mode(self, mode):
        self.auto_mode = mode

    def set_target(self, target):
        self.target_joint_dest = list(target)

    def update(self, current_joints):
        """Advance joints one step toward target.

        Returns (new_joints, arrived). In manual mode returns current_joints
        unchanged and arrived=False.

        Hybrid law: proportional approach capped by MAX_STEP. This gives a
        fast constant-velocity cruise on long moves and a smooth proportional
        landing near the target - no exponential tail.
        """
        if self.auto_mode not in (MODE_AUTO_PDF, MODE_AUTO_HOME):
            return current_joints, False
        if not self.target_joint_dest:
            return current_joints, False

        new_joints = list(current_joints)
        max_error = 0.0

        for i in range(6):
            diff = self.target_joint_dest[i] - current_joints[i]
            max_error = max(max_error, abs(diff))
            # Proportional step, then clamp to MAX_STEP for the cruise phase.
            step = float(np.clip(diff * self.SPEED, -self.MAX_STEP, self.MAX_STEP))
            low, up = self.sim.joint_limits[i]
            new_joints[i] = float(np.clip(current_joints[i] + step, low, up))
            self.sim.set_joint_position(i, new_joints[i])

        arrived = max_error < self.ARRIVAL_THRESHOLD
        return new_joints, arrived
