import numpy as np
import matplotlib.pyplot as plt

# Distance from the J6 frame to the end-effector flange (from PAROL6 URDF link CoM data).
_FLANGE_OFFSET = 0.055  # metres along T6's local -Z axis


def generate_wireframe_image(chain, filename):
    # chain[0] = base, chain[1..6] = J1..J6 (J5 and J6 share the same XYZ in the URDF).
    # We extend T6 by the flange offset to get a spatially distinct J6 position.
    T6 = chain[-1]
    tcp = (T6 @ np.array([0.0, 0.0, -_FLANGE_OFFSET, 1.0]))[:3]

    # Skeleton positions: base → J1 → J2 → J3 → J4 → J5 → J6(tcp)
    xs = [T[0, 3] for T in chain[1:]]  # J1..J5 from chain, J6 replaced by tcp
    ys = [T[1, 3] for T in chain[1:]]
    zs = [T[2, 3] for T in chain[1:]]
    # Replace last point (chain[6], same as chain[5]) with the real flange position
    xs[-1], ys[-1], zs[-1] = float(tcp[0]), float(tcp[1]), float(tcp[2])

    # Include base as line start (not a motor, just the mounting point)
    line_xs = [chain[0][0, 3]] + xs
    line_ys = [chain[0][1, 3]] + ys
    line_zs = [chain[0][2, 3]] + zs

    fig = plt.figure(figsize=(4, 4))
    ax = fig.add_subplot(111, projection="3d")

    # Connecting lines: base → J1 → … → J6
    ax.plot(line_xs, line_ys, line_zs, "-", color="#1a73e8", lw=3)

    # J1–J5: red circles (xs[0:5], ys[0:5], zs[0:5])
    ax.scatter(xs[:5], ys[:5], zs[:5],
               color="#d93025", s=80, marker="o", zorder=10, label="J1–J5")

    # J6 / TCP: green circle at flange position (xs[5], ys[5], zs[5])
    ax.scatter([xs[5]], [ys[5]], [zs[5]],
               color="#34a853", s=100, marker="o", zorder=11, label="J6 / TCP")

    ax.set_xlim([-0.5, 0.5])
    ax.set_ylim([-0.5, 0.5])
    ax.set_zlim([0, 0.7])
    ax.set_title("Reconstrucción Analítica (6 Eslabones)")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.legend(fontsize=8, loc="upper right")
    plt.savefig(filename, bbox_inches="tight", dpi=150)
    plt.close(fig)


def capture_snapshot(snap_index, current_q_img, current_chain,
                     current_T_matrix, current_euler, current_joints_state):
    img_sim_path  = f"snap_sim_{snap_index}.png"
    img_wire_path = f"snap_wire_{snap_index}.png"

    if current_q_img:
        current_q_img.save(img_sim_path)

    generate_wireframe_image(current_chain, img_wire_path)

    return {
        "sim_img":  img_sim_path,
        "wire_img": img_wire_path,
        "T_matrix": current_T_matrix.copy(),
        "R_matrix": current_T_matrix[:3, :3].copy(),
        "euler":    current_euler.copy(),
        "joints":   list(current_joints_state),
    }
