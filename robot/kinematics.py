import numpy as np


def get_rot_z(angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])


def urdf_tf(xyz, rpy, joint_angle, axis_sign):
    T = np.eye(4)
    T[:3, 3] = xyz
    r, p_y, y = rpy
    Rx = np.array([
        [1, 0, 0, 0],
        [0, np.cos(r), -np.sin(r), 0],
        [0, np.sin(r), np.cos(r), 0],
        [0, 0, 0, 1],
    ])
    Ry = np.array([
        [np.cos(p_y), 0, np.sin(p_y), 0],
        [0, 1, 0, 0],
        [-np.sin(p_y), 0, np.cos(p_y), 0],
        [0, 0, 0, 1],
    ])
    Rz = np.array([
        [np.cos(y), -np.sin(y), 0, 0],
        [np.sin(y), np.cos(y), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ])
    return T @ Rz @ Ry @ Rx @ get_rot_z(joint_angle * axis_sign)


def get_kinematic_chain(joints):
    """Returns list of 4x4 homogeneous transforms from base to each link (PAROL6 DH)."""
    j1, j2, j3, j4, j5, j6 = joints
    chain = [np.eye(4)]
    T1 = chain[0] @ urdf_tf([0, 0, 0], [0, 0, 0], j1, 1)
    chain.append(T1)
    T2 = T1 @ urdf_tf([0.0234207, 0, 0.1105], [-1.5707963, 0, 0], j2, 1)
    chain.append(T2)
    T3 = T2 @ urdf_tf([0, -0.18, 0], [np.pi, 0, -np.pi / 2], j3, -1)
    chain.append(T3)
    T4 = T3 @ urdf_tf([0.0435, 0, 0], [np.pi / 2, 0, np.pi], j4, -1)
    chain.append(T4)
    T5 = T4 @ urdf_tf([0, 0, -0.17635], [-np.pi / 2, 0, 0], j5, -1)
    chain.append(T5)
    T6 = T5 @ urdf_tf([0, 0, 0], [np.pi / 2, 0, 0], j6, -1)
    chain.append(T6)
    return chain


def get_euler_angles(R):
    """Extract ZYX Euler angles from a 3x3 rotation matrix."""
    sy = np.sqrt(R[0, 0] ** 2 + R[1, 0] ** 2)
    if sy >= 1e-6:
        x = np.arctan2(R[2, 1], R[2, 2])
        y = np.arctan2(-R[2, 0], sy)
        z = np.arctan2(R[1, 0], R[0, 0])
    else:
        x = np.arctan2(-R[1, 2], R[1, 1])
        y = np.arctan2(-R[2, 0], sy)
        z = 0.0
    return np.array([x, y, z])
