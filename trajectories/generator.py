import random
import numpy as np

_PREDEFINED = {
    1: {
        "name": "Trayectoria 1 (Pick & Place)",
        "poses": [
            [0.0, -0.5, 0.5, 0.0, 0.0, 0.0],
            [0.8, -0.2, 0.8, -0.5, 0.2, 0.0],
            [0.8, -0.5, 0.5, 0.0, 0.0, 0.0],
        ],
    },
    2: {
        "name": "Trayectoria 2 (Inspección)",
        "poses": [
            [-0.5, 0.2, -0.2, 0.5, -0.5, 0.5],
            [0.0, 0.5, -0.5, 0.0, 0.5, 0.0],
            [0.5, 0.2, -0.2, -0.5, -0.5, -0.5],
        ],
    },
    3: {
        "name": "Trayectoria 3 (Esquivar)",
        "poses": [
            [0.2, 0.2, 0.2, 0.2, 0.2, 0.2],
            [-0.2, -0.2, -0.2, -0.2, -0.2, -0.2],
            [0.0, 0.5, -0.5, 0.0, 0.0, 0.0],
        ],
    },
}


def get_trajectory(traj_id, joint_limits):
    """Return (name, poses) for a predefined trajectory, clipped to joint limits."""
    entry = _PREDEFINED[traj_id]
    poses = [_clip_pose(p, joint_limits) for p in entry["poses"]]
    return entry["name"], poses


def build_manual_trajectory(current_joints, target_joints, joint_limits):
    """Build a 3-pose trajectory: current → midpoint → target."""
    midpoint = [(current_joints[i] + target_joints[i]) / 2.0 for i in range(6)]
    poses = [list(current_joints), midpoint, list(target_joints)]
    return "Viaje a Pose Manual", [_clip_pose(p, joint_limits) for p in poses]


def interpolate_trajectory(poses, steps_per_segment=25):
    """Linearly interpolate between consecutive poses to form a dense trajectory."""
    if len(poses) < 2:
        return [list(poses[0])] if poses else []
    points = []
    for i in range(len(poses) - 1):
        a = np.array(poses[i])
        b = np.array(poses[i + 1])
        include_end = (i == len(poses) - 2)
        for t in np.linspace(0.0, 1.0, steps_per_segment, endpoint=include_end):
            points.append((a + t * (b - a)).tolist())
    points.append(list(poses[-1]))
    return points


def sample_snapshot_waypoints(trajectory, n=3):
    """
    Pick n random, ordered waypoints from the trajectory — one per segment,
    avoiding segment boundaries so points are truly interior to the trajectory.
    """
    total = len(trajectory)
    if total < n * 3:
        # Fallback when trajectory is too short: uniform spacing
        step = max(1, (total - 1) // (n - 1))
        return [trajectory[min(i * step, total - 1)] for i in range(n)]

    seg = total // n
    buffer = max(1, seg // 5)  # 20% buffer to avoid segment edges
    waypoints = []
    for s in range(n):
        lo = s * seg + buffer
        hi = min((s + 1) * seg - buffer, total - 1)
        lo = min(lo, hi)
        idx = random.randint(lo, hi)
        waypoints.append(trajectory[idx])
    return waypoints


def _clip_pose(pose, joint_limits):
    return [
        float(np.clip(pose[i], joint_limits[i][0], joint_limits[i][1]))
        for i in range(6)
    ]
