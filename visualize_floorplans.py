#!/usr/bin/env python3
"""
Visualize floor plan configurations as colored geometric drawings.
Generates a PNG with the top configurations side-by-side.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

from floor_configurations import derive_room_specs, generate_configurations, FURNITURE

# ── Room colors ──
ROOM_COLORS = {
    "bedroom1":  "#7FB3D8",   # soft blue
    "bedroom2":  "#6CA0C8",   # slightly deeper blue
    "bathroom1": "#A8D8A8",   # soft green
    "bathroom2": "#8FC98F",   # slightly deeper green
    "kitchen":   "#F4C478",   # warm amber
    "entrance":  "#D4A0D4",   # soft purple
}

ROOM_LABELS = {
    "bedroom1":  "Bedroom 1",
    "bedroom2":  "Bedroom 2",
    "bathroom1": "Bath 1",
    "bathroom2": "Bath 2",
    "kitchen":   "Kitchen",
    "entrance":  "Entry",
}

# Furniture to sketch inside rooms (simplified rectangles)
FURNITURE_SKETCHES = {
    "bedroom1": [
        ("Bed",     0.5, 0.5, 4.5, 6.5, "#4A7A9B"),
        ("Nightstand", 5.2, 0.5, 1.5, 1.5, "#8B6F4E"),
        ("Dresser", 0.5, 7.3, 3.0, 1.2, "#8B6F4E"),
        ("Desk",    5.0, 3.0, 2.5, 2.0, "#8B6F4E"),
    ],
    "bedroom2": [
        ("Bed",     0.5, 0.5, 4.5, 6.5, "#4A7A9B"),
        ("Nightstand", 5.2, 0.5, 1.5, 1.5, "#8B6F4E"),
        ("Dresser", 0.5, 7.3, 3.0, 1.2, "#8B6F4E"),
        ("Desk",    5.0, 3.0, 2.5, 2.0, "#8B6F4E"),
    ],
    "bathroom1": [
        ("Shower",  0.3, 0.3, 3.0, 3.0, "#B0D4F1"),
        ("Toilet",  0.3, 3.8, 1.5, 2.5, "#E8E8E8"),
        ("Vanity",  2.5, 4.5, 2.0, 1.5, "#D4B896"),
    ],
    "bathroom2": [
        ("Shower",  0.3, 0.3, 3.0, 3.0, "#B0D4F1"),
        ("Toilet",  0.3, 3.8, 1.5, 2.5, "#E8E8E8"),
        ("Vanity",  2.5, 4.5, 2.0, 1.5, "#D4B896"),
    ],
    "kitchen": [
        ("Counter", 0.3, 0.3, 6.0, 2.0, "#C4A882"),
        ("Fridge",  6.5, 0.3, 1.0, 2.5, "#D0D0D0"),
        ("Stove",   0.3, 2.8, 2.5, 2.0, "#888888"),
        ("Sink",    3.2, 2.8, 2.0, 1.8, "#B0D4F1"),
        ("Table",   1.0, 5.5, 3.0, 2.0, "#8B6F4E"),
    ],
    "entrance": [
        ("Door",    0.5, 0.2, 3.0, 0.4, "#6B4226"),
        ("Bench",   0.5, 1.5, 3.0, 1.2, "#8B6F4E"),
        ("Hooks",   0.3, 3.2, 3.0, 0.3, "#555555"),
    ],
}


def draw_room_detail(ax, room, draw_furniture=True):
    """Draw a single room rectangle with fill, border, label, and furniture."""
    color = ROOM_COLORS.get(room.name, "#DDDDDD")
    label = ROOM_LABELS.get(room.name, room.name)

    # Room fill
    rect = mpatches.FancyBboxPatch(
        (room.x, room.y), room.w, room.d,
        boxstyle="round,pad=0.05",
        facecolor=color, edgecolor="#333333", linewidth=1.5, alpha=0.85
    )
    ax.add_patch(rect)

    # Room label
    cx = room.x + room.w / 2
    cy = room.y + room.d / 2
    ax.text(cx, cy + 0.4, label, ha='center', va='center',
            fontsize=9, fontweight='bold', color='#222222')
    ax.text(cx, cy - 0.4, f"{room.w:.0f}′×{room.d:.0f}′ = {room.w*room.d:.0f} sf",
            ha='center', va='center', fontsize=7, color='#444444')

    # Furniture sketches
    if draw_furniture and room.name in FURNITURE_SKETCHES:
        # Scale furniture to fit if room is rotated
        specs = FURNITURE_SKETCHES[room.name]
        # We need to figure out the "native" room size vs actual
        # Native sizes from the spec: bedroom 8×9, bath 5×7, kitchen 7×8, entrance 4×4
        native_sizes = {
            "bedroom1": (8, 9), "bedroom2": (8, 9),
            "bathroom1": (5, 7), "bathroom2": (5, 7),
            "kitchen": (7, 8), "entrance": (4, 4),
        }
        nw, nd = native_sizes.get(room.name, (room.w, room.d))
        sx = room.w / nw
        sy = room.d / nd

        for fname, fx, fy, fw, fd, fc in specs:
            frect = mpatches.Rectangle(
                (room.x + fx * sx, room.y + fy * sy),
                fw * sx, fd * sy,
                facecolor=fc, edgecolor="#555555", linewidth=0.6, alpha=0.55
            )
            ax.add_patch(frect)
            # tiny label
            ax.text(room.x + (fx + fw/2) * sx, room.y + (fy + fd/2) * sy,
                    fname, ha='center', va='center', fontsize=4.5,
                    color='#222222', alpha=0.8)


def draw_config(ax, cfg, title_extra="", draw_furniture=True):
    """Draw a full configuration on a matplotlib Axes."""
    # Outer boundary
    outer = mpatches.Rectangle(
        (0, 0), cfg.bounding_w, cfg.bounding_d,
        facecolor='#F5F0E8', edgecolor='#222222', linewidth=2.5
    )
    ax.add_patch(outer)

    for room in cfg.rooms:
        draw_room_detail(ax, room, draw_furniture=draw_furniture)

    # Dimension annotations
    # Bottom width
    ax.annotate('', xy=(cfg.bounding_w, -1.2), xytext=(0, -1.2),
                arrowprops=dict(arrowstyle='<->', color='#333', lw=1.2))
    ax.text(cfg.bounding_w / 2, -1.8, f"{cfg.bounding_w:.1f}′",
            ha='center', va='center', fontsize=8, color='#333')

    # Left height
    ax.annotate('', xy=(-1.2, cfg.bounding_d), xytext=(-1.2, 0),
                arrowprops=dict(arrowstyle='<->', color='#333', lw=1.2))
    ax.text(-2.0, cfg.bounding_d / 2, f"{cfg.bounding_d:.1f}′",
            ha='center', va='center', fontsize=8, color='#333', rotation=90)

    # Title
    short_label = cfg.label.split(":")[0].strip()
    ax.set_title(
        f"{title_extra}{short_label}\n"
        f"{cfg.bounding_w:.1f}′ × {cfg.bounding_d:.1f}′ = {cfg.total_area:.0f} sf  "
        f"({cfg.efficiency:.0f}% eff)",
        fontsize=10, fontweight='bold', pad=10
    )

    ax.set_xlim(-3, cfg.bounding_w + 2)
    ax.set_ylim(-3, cfg.bounding_d + 2)
    ax.set_aspect('equal')
    ax.axis('off')


def main():
    specs = derive_room_specs()
    configs = generate_configurations(specs)

    # ── Figure 1: Top 4 configs overview ──
    top_n = min(4, len(configs))
    fig, axes = plt.subplots(1, top_n, figsize=(7 * top_n, 12))
    if top_n == 1:
        axes = [axes]

    fig.suptitle(
        "Backyard Suite — Floor Plan Configurations (≤ 430 sq ft)\n"
        "6 rooms: 2 bedrooms, 2 bathrooms, 1 kitchen, 1 entrance",
        fontsize=14, fontweight='bold', y=0.98
    )

    for i, cfg in enumerate(configs[:top_n]):
        draw_config(axes[i], cfg, title_extra=f"Config {i+1}: ", draw_furniture=False)

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig("floorplan_overview.png", dpi=150, bbox_inches='tight',
                facecolor='white')
    print(f"Saved: floorplan_overview.png  ({top_n} configs)")

    # ── Figure 2: Best config with furniture detail ──
    best = configs[0]
    fig2, ax2 = plt.subplots(1, 1, figsize=(12, 10))
    fig2.suptitle(
        "Best Configuration — Detailed View with Furniture",
        fontsize=14, fontweight='bold', y=0.98
    )
    draw_config(ax2, best, title_extra="Config 1: ", draw_furniture=True)

    # Legend
    legend_patches = [
        mpatches.Patch(facecolor=c, edgecolor='#333', label=ROOM_LABELS[n])
        for n, c in ROOM_COLORS.items()
    ]
    ax2.legend(handles=legend_patches, loc='upper right', fontsize=8,
               framealpha=0.9, title="Rooms")

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    fig2.savefig("floorplan_detail.png", dpi=150, bbox_inches='tight',
                 facecolor='white')
    print(f"Saved: floorplan_detail.png  (best config with furniture)")

    # ── Figure 3: All unique layout shapes comparison ──
    # Group by distinct bounding dimensions
    seen_shapes = {}
    for cfg in configs:
        key = (cfg.bounding_w, cfg.bounding_d)
        if key not in seen_shapes:
            seen_shapes[key] = cfg

    shape_list = list(seen_shapes.values())[:6]
    ncols = min(3, len(shape_list))
    nrows = (len(shape_list) + ncols - 1) // ncols
    fig3, axes3 = plt.subplots(nrows, ncols, figsize=(7 * ncols, 10 * nrows))
    if nrows == 1 and ncols == 1:
        axes3 = np.array([[axes3]])
    elif nrows == 1:
        axes3 = axes3.reshape(1, -1)
    elif ncols == 1:
        axes3 = axes3.reshape(-1, 1)

    fig3.suptitle(
        "Comparison of Distinct Bounding Shapes",
        fontsize=14, fontweight='bold', y=0.99
    )

    for idx, cfg in enumerate(shape_list):
        r, c = divmod(idx, ncols)
        draw_config(axes3[r][c], cfg, title_extra=f"Shape {idx+1}: ",
                    draw_furniture=False)

    # Hide unused axes
    for idx in range(len(shape_list), nrows * ncols):
        r, c = divmod(idx, ncols)
        axes3[r][c].axis('off')

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig3.savefig("floorplan_shapes.png", dpi=150, bbox_inches='tight',
                 facecolor='white')
    print(f"Saved: floorplan_shapes.png  ({len(shape_list)} distinct shapes)")


if __name__ == "__main__":
    main()
