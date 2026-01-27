"""
3D Orbital Visualizations for Homework 1
SPCE 5025 - Fundamentals of Astronautics

Generates 3D plots of orbits computed from state vectors, showing:
- Full orbital trajectories
- Earth reference sphere
- Periapsis and apoapsis markers
- Ascending/descending nodes
- Current spacecraft position
- Orbital plane orientation

Author: Student Implementation
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from typing import Tuple, Optional
from dataclasses import dataclass

# Import the solution module for orbital element computation
from hw1_solution import state_to_keplerian, KeplerianElements

# ============================================================================
# CONSTANTS
# ============================================================================

MU_EARTH = 3.986004418e14  # m^3/s^2
R_EARTH = 6.371e6  # Earth's mean radius [m]


# ============================================================================
# COORDINATE TRANSFORMATIONS
# ============================================================================

def keplerian_to_position(elements: KeplerianElements, nu: float) -> np.ndarray:
    """
    Convert Keplerian elements to position vector at a given true anomaly.

    Parameters
    ----------
    elements : KeplerianElements
        Orbital elements (uses a, e, inc, raan, omega)
    nu : float
        True anomaly [rad]

    Returns
    -------
    np.ndarray
        Position vector in ECI frame [m]
    """
    # Semi-latus rectum
    p = elements.a * (1 - elements.e**2)

    # Radius at this true anomaly
    r = p / (1 + elements.e * np.cos(nu))

    # Position in perifocal (PQW) frame
    # P points to periapsis, Q is 90 deg ahead in orbital plane
    r_pqw = r * np.array([np.cos(nu), np.sin(nu), 0.0])

    # Rotation matrix from perifocal to ECI
    # R = R3(-RAAN) @ R1(-inc) @ R3(-omega)
    cos_O = np.cos(elements.raan)
    sin_O = np.sin(elements.raan)
    cos_i = np.cos(elements.inc)
    sin_i = np.sin(elements.inc)
    cos_w = np.cos(elements.omega)
    sin_w = np.sin(elements.omega)

    # Combined rotation matrix (perifocal to ECI)
    R = np.array([
        [cos_O*cos_w - sin_O*sin_w*cos_i, -cos_O*sin_w - sin_O*cos_w*cos_i,  sin_O*sin_i],
        [sin_O*cos_w + cos_O*sin_w*cos_i, -sin_O*sin_w + cos_O*cos_w*cos_i, -cos_O*sin_i],
        [sin_w*sin_i,                      cos_w*sin_i,                       cos_i]
    ])

    return R @ r_pqw


def generate_orbit_points(elements: KeplerianElements,
                          num_points: int = 360) -> np.ndarray:
    """
    Generate position vectors around the entire orbit.

    Parameters
    ----------
    elements : KeplerianElements
        Orbital elements
    num_points : int
        Number of points to generate around the orbit

    Returns
    -------
    np.ndarray
        Array of shape (num_points, 3) with position vectors [m]
    """
    nu_values = np.linspace(0, 2*np.pi, num_points)
    positions = np.array([keplerian_to_position(elements, nu) for nu in nu_values])
    return positions


def get_node_positions(elements: KeplerianElements) -> Tuple[np.ndarray, np.ndarray]:
    """
    Get positions of ascending and descending nodes.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        (ascending_node_position, descending_node_position) in ECI [m]
    """
    # True anomaly at ascending node: nu = -omega (or 2*pi - omega)
    nu_ascending = -elements.omega
    if nu_ascending < 0:
        nu_ascending += 2*np.pi

    # True anomaly at descending node: nu = pi - omega
    nu_descending = np.pi - elements.omega
    if nu_descending < 0:
        nu_descending += 2*np.pi

    pos_ascending = keplerian_to_position(elements, nu_ascending)
    pos_descending = keplerian_to_position(elements, nu_descending)

    return pos_ascending, pos_descending


# ============================================================================
# PLOTTING FUNCTIONS
# ============================================================================

def create_earth_sphere(ax: Axes3D, scale: float = 1.0,
                        alpha: float = 0.3) -> None:
    """
    Add a wireframe Earth sphere to the 3D axes.

    Parameters
    ----------
    ax : Axes3D
        Matplotlib 3D axes
    scale : float
        Scale factor for visualization (orbit positions should use same scale)
    alpha : float
        Transparency of the sphere
    """
    u = np.linspace(0, 2*np.pi, 30)
    v = np.linspace(0, np.pi, 20)

    x = R_EARTH * scale * np.outer(np.cos(u), np.sin(v))
    y = R_EARTH * scale * np.outer(np.sin(u), np.sin(v))
    z = R_EARTH * scale * np.outer(np.ones(np.size(u)), np.cos(v))

    ax.plot_surface(x, y, z, color='royalblue', alpha=alpha,
                    linewidth=0, antialiased=True)


def plot_reference_axes(ax: Axes3D, length: float) -> None:
    """
    Plot ECI reference axes (X, Y, Z).

    Parameters
    ----------
    ax : Axes3D
        Matplotlib 3D axes
    length : float
        Length of axis arrows
    """
    # X-axis (vernal equinox direction)
    ax.quiver(0, 0, 0, length, 0, 0, color='red', arrow_length_ratio=0.1,
              linewidth=2, label='X (Vernal Equinox)')
    # Y-axis
    ax.quiver(0, 0, 0, 0, length, 0, color='green', arrow_length_ratio=0.1,
              linewidth=2, label='Y')
    # Z-axis (Earth's spin axis)
    ax.quiver(0, 0, 0, 0, 0, length, color='blue', arrow_length_ratio=0.1,
              linewidth=2, label='Z (North Pole)')


def plot_single_orbit(ax: Axes3D, elements: KeplerianElements,
                      r_current: np.ndarray, name: str,
                      color: str, scale: float = 1e-6) -> None:
    """
    Plot a single orbit with all key features.

    Parameters
    ----------
    ax : Axes3D
        Matplotlib 3D axes
    elements : KeplerianElements
        Computed orbital elements
    r_current : np.ndarray
        Current position vector [m]
    name : str
        Label for the orbit
    color : str
        Color for this orbit
    scale : float
        Scale factor to convert meters to plot units (default: 1e-6 for Mm)
    """
    # Generate orbit trajectory
    orbit_points = generate_orbit_points(elements) * scale

    # Plot orbit path
    ax.plot(orbit_points[:, 0], orbit_points[:, 1], orbit_points[:, 2],
            color=color, linewidth=1.5, label=f'{name} Orbit')

    # Current position
    r_scaled = r_current * scale
    ax.scatter(*r_scaled, color=color, s=100, marker='o',
               edgecolors='black', linewidths=1, zorder=5)

    # Periapsis (nu = 0)
    r_periapsis = keplerian_to_position(elements, 0.0) * scale
    ax.scatter(*r_periapsis, color=color, s=80, marker='^',
               edgecolors='black', linewidths=1, zorder=5)

    # Apoapsis (nu = pi)
    r_apoapsis = keplerian_to_position(elements, np.pi) * scale
    ax.scatter(*r_apoapsis, color=color, s=80, marker='v',
               edgecolors='black', linewidths=1, zorder=5)

    # Ascending node
    if elements.inc > 0.01:  # Only plot nodes for non-equatorial orbits
        r_asc, r_desc = get_node_positions(elements)
        r_asc_scaled = r_asc * scale
        ax.scatter(*r_asc_scaled, color='yellow', s=60, marker='D',
                   edgecolors='black', linewidths=1, zorder=5)


def visualize_all_orbits(test_cases: list, figsize: Tuple[int, int] = (16, 12)) -> plt.Figure:
    """
    Create a comprehensive visualization of all orbits.

    Parameters
    ----------
    test_cases : list
        List of dictionaries with 'name', 'r', 'v' keys
    figsize : Tuple[int, int]
        Figure size in inches

    Returns
    -------
    plt.Figure
        Matplotlib figure object
    """
    fig = plt.figure(figsize=figsize)

    # Color palette for different orbits
    colors = ['crimson', 'forestgreen', 'darkorange', 'purple']

    # Scale factor: convert meters to megameters (Mm) for readability
    scale = 1e-6

    # Compute all orbital elements and find max radius for axis scaling
    all_elements = []
    max_radius = 0
    for case in test_cases:
        elements = state_to_keplerian(case['r'], case['v'], MU_EARTH)
        all_elements.append(elements)
        max_radius = max(max_radius, elements.r_apoapsis)

    axis_limit = max_radius * scale * 1.1

    # ========================================================================
    # Main 3D plot with all orbits
    # ========================================================================
    ax_main = fig.add_subplot(2, 2, 1, projection='3d')
    ax_main.set_title('All Orbits - 3D View', fontsize=12, fontweight='bold')

    # Add Earth
    create_earth_sphere(ax_main, scale=scale, alpha=0.4)

    # Add reference axes
    plot_reference_axes(ax_main, axis_limit * 0.3)

    # Plot each orbit
    for i, (case, elements, color) in enumerate(zip(test_cases, all_elements, colors)):
        plot_single_orbit(ax_main, elements, case['r'], case['name'], color, scale)

    ax_main.set_xlabel('X [Mm]', fontsize=10)
    ax_main.set_ylabel('Y [Mm]', fontsize=10)
    ax_main.set_zlabel('Z [Mm]', fontsize=10)
    ax_main.set_xlim(-axis_limit, axis_limit)
    ax_main.set_ylim(-axis_limit, axis_limit)
    ax_main.set_zlim(-axis_limit, axis_limit)
    ax_main.legend(loc='upper left', fontsize=8)

    # ========================================================================
    # XY plane view (equatorial)
    # ========================================================================
    ax_xy = fig.add_subplot(2, 2, 2, projection='3d')
    ax_xy.set_title('Equatorial Plane View (Looking Down Z-axis)', fontsize=12, fontweight='bold')

    create_earth_sphere(ax_xy, scale=scale, alpha=0.4)
    for i, (case, elements, color) in enumerate(zip(test_cases, all_elements, colors)):
        plot_single_orbit(ax_xy, elements, case['r'], case['name'], color, scale)

    ax_xy.view_init(elev=90, azim=0)  # Looking down Z-axis
    ax_xy.set_xlabel('X [Mm]', fontsize=10)
    ax_xy.set_ylabel('Y [Mm]', fontsize=10)
    ax_xy.set_zlabel('Z [Mm]', fontsize=10)
    ax_xy.set_xlim(-axis_limit, axis_limit)
    ax_xy.set_ylim(-axis_limit, axis_limit)
    ax_xy.set_zlim(-axis_limit, axis_limit)

    # ========================================================================
    # XZ plane view
    # ========================================================================
    ax_xz = fig.add_subplot(2, 2, 3, projection='3d')
    ax_xz.set_title('Side View (Looking Along Y-axis)', fontsize=12, fontweight='bold')

    create_earth_sphere(ax_xz, scale=scale, alpha=0.4)
    for i, (case, elements, color) in enumerate(zip(test_cases, all_elements, colors)):
        plot_single_orbit(ax_xz, elements, case['r'], case['name'], color, scale)

    ax_xz.view_init(elev=0, azim=0)  # Looking along Y-axis
    ax_xz.set_xlabel('X [Mm]', fontsize=10)
    ax_xz.set_ylabel('Y [Mm]', fontsize=10)
    ax_xz.set_zlabel('Z [Mm]', fontsize=10)
    ax_xz.set_xlim(-axis_limit, axis_limit)
    ax_xz.set_ylim(-axis_limit, axis_limit)
    ax_xz.set_zlim(-axis_limit, axis_limit)

    # ========================================================================
    # Orbital parameters summary table
    # ========================================================================
    ax_table = fig.add_subplot(2, 2, 4)
    ax_table.axis('off')
    ax_table.set_title('Orbital Parameters Summary', fontsize=12, fontweight='bold')

    # Create table data
    headers = ['Parameter', 'Vector 1', 'Vector 2', 'Vector 3', 'Vector 4']
    table_data = [
        ['a [km]'] + [f'{e.a/1000:.1f}' for e in all_elements],
        ['e'] + [f'{e.e:.6f}' for e in all_elements],
        ['i [deg]'] + [f'{np.degrees(e.inc):.2f}' for e in all_elements],
        ['Ω [deg]'] + [f'{np.degrees(e.raan):.2f}' for e in all_elements],
        ['ω [deg]'] + [f'{np.degrees(e.omega):.2f}' for e in all_elements],
        ['ν [deg]'] + [f'{np.degrees(e.nu):.2f}' for e in all_elements],
        ['T [hr]'] + [f'{e.period/3600:.2f}' for e in all_elements],
        ['rp [km]'] + [f'{e.r_periapsis/1000:.1f}' for e in all_elements],
        ['ra [km]'] + [f'{e.r_apoapsis/1000:.1f}' for e in all_elements],
    ]

    table = ax_table.table(cellText=table_data, colLabels=headers,
                           loc='center', cellLoc='center',
                           colColours=['lightgray']*5)
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 1.5)

    # Color-code the orbit columns
    for i, color in enumerate(colors):
        for j in range(len(table_data) + 1):
            table[(j, i+1)].set_facecolor(plt.cm.colors.to_rgba(color, alpha=0.15))

    plt.tight_layout()
    return fig


def visualize_individual_orbits(test_cases: list) -> plt.Figure:
    """
    Create individual detailed plots for each orbit.

    Parameters
    ----------
    test_cases : list
        List of dictionaries with 'name', 'r', 'v' keys

    Returns
    -------
    plt.Figure
        Matplotlib figure object
    """
    fig = plt.figure(figsize=(16, 12))
    colors = ['crimson', 'forestgreen', 'darkorange', 'purple']
    scale = 1e-6

    for idx, (case, color) in enumerate(zip(test_cases, colors)):
        elements = state_to_keplerian(case['r'], case['v'], MU_EARTH)

        ax = fig.add_subplot(2, 2, idx + 1, projection='3d')

        # Set axis limit based on this orbit's apoapsis
        axis_limit = elements.r_apoapsis * scale * 1.2

        # Add Earth (scaled appropriately for each orbit)
        create_earth_sphere(ax, scale=scale, alpha=0.5)

        # Plot the orbit
        plot_single_orbit(ax, elements, case['r'], case['name'], color, scale)

        # Add velocity vector at current position
        v_scale = axis_limit * 0.15 / np.linalg.norm(case['v'])  # Scale for visibility
        r_scaled = case['r'] * scale
        v_scaled = case['v'] * v_scale
        ax.quiver(*r_scaled, *v_scaled, color='cyan', arrow_length_ratio=0.2,
                  linewidth=2, label='Velocity')

        # Title with key parameters
        title = (f"{case['name']}\n"
                f"a={elements.a/1000:.0f} km, e={elements.e:.4f}, "
                f"i={np.degrees(elements.inc):.1f}°")
        ax.set_title(title, fontsize=10, fontweight='bold')

        ax.set_xlabel('X [Mm]', fontsize=9)
        ax.set_ylabel('Y [Mm]', fontsize=9)
        ax.set_zlabel('Z [Mm]', fontsize=9)
        ax.set_xlim(-axis_limit, axis_limit)
        ax.set_ylim(-axis_limit, axis_limit)
        ax.set_zlim(-axis_limit, axis_limit)

        # Add legend for markers
        ax.scatter([], [], color=color, marker='o', s=60, label='Current Position')
        ax.scatter([], [], color=color, marker='^', s=60, label='Periapsis')
        ax.scatter([], [], color=color, marker='v', s=60, label='Apoapsis')
        if elements.inc > 0.01:
            ax.scatter([], [], color='yellow', marker='D', s=40, label='Ascending Node')
        ax.legend(loc='upper left', fontsize=7)

    plt.tight_layout()
    return fig


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Generate all visualizations for homework orbits."""

    # Test vectors from homework
    test_cases = [
        {
            'name': 'Vector 1',
            'r': np.array([-464836.978606, -6191644.716805, -2961635.481039]),
            'v': np.array([7322.77235464, 406.01896116, -1910.89281450])
        },
        {
            'name': 'Vector 2',
            'r': np.array([572461.711228, -1015437.194396, 7707337.871302]),
            'v': np.array([-6195.262945, -3575.889650, -5.423283])
        },
        {
            'name': 'Vector 3',
            'r': np.array([-5142754.617115, 16130814.767566, 20434322.229790]),
            'v': np.array([-2924.287128, -2303.326264, 1084.798834])
        },
        {
            'name': 'Vector 4',
            'r': np.array([-21100299.894024, 36462486.120500, 69117.555126]),
            'v': np.array([-2664.268125, -1539.996659, 1.834442])
        }
    ]

    print("=" * 70)
    print("SPCE 5025 - HOMEWORK 1 ORBITAL VISUALIZATIONS")
    print("=" * 70)

    # Generate combined view
    print("\nGenerating combined orbit visualization...")
    fig1 = visualize_all_orbits(test_cases)
    fig1.savefig('hw1_orbits_combined.png', dpi=150, bbox_inches='tight',
                 facecolor='white', edgecolor='none')
    print("  Saved: hw1_orbits_combined.png")

    # Generate individual orbit views
    print("\nGenerating individual orbit visualizations...")
    fig2 = visualize_individual_orbits(test_cases)
    fig2.savefig('hw1_orbits_individual.png', dpi=150, bbox_inches='tight',
                 facecolor='white', edgecolor='none')
    print("  Saved: hw1_orbits_individual.png")

    print("\n" + "=" * 70)
    print("VISUALIZATION COMPLETE")
    print("=" * 70)
    print("\nMarker Legend:")
    print("  ● Circle    = Current spacecraft position")
    print("  ▲ Triangle  = Periapsis (closest approach)")
    print("  ▼ Triangle  = Apoapsis (farthest point)")
    print("  ◆ Diamond   = Ascending node")
    print("  → Arrow     = Velocity vector (individual plots)")
    print("\nDisplaying plots...")

    plt.show()


if __name__ == "__main__":
    main()
