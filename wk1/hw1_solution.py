"""
Keplerian Orbital Elements from State Vectors
SPCE 5025 - Fundamentals of Astronautics - Homework 1

Converts Earth-Centered Inertial (ECI) position/velocity state vectors
to classical Keplerian orbital elements using angular momentum and
eccentricity vector formulations.

Author: Student Solution (independent implementation)
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class KeplerianElements:
    """Container for classical orbital elements and derived quantities."""
    a: float       # Semi-major axis [m]
    e: float       # Eccentricity [dimensionless]
    inc: float     # Inclination [rad]
    raan: float    # Right Ascension of Ascending Node [rad]
    omega: float   # Argument of periapsis [rad]
    nu: float      # True anomaly [rad]
    period: float  # Orbital period [s]
    r_periapsis: float  # Periapsis radius [m]
    r_apoapsis: float   # Apoapsis radius [m]

    def to_degrees(self) -> dict:
        """Return angular elements in degrees for display."""
        return {
            'a_m': self.a,
            'e': self.e,
            'inc_deg': np.degrees(self.inc),
            'raan_deg': np.degrees(self.raan),
            'omega_deg': np.degrees(self.omega),
            'nu_deg': np.degrees(self.nu),
            'period_s': self.period,
            'r_periapsis_m': self.r_periapsis,
            'r_apoapsis_m': self.r_apoapsis
        }

# ============================================================================
# CORE CONVERSION FUNCTION
# ============================================================================

def state_to_keplerian(r_vec: np.ndarray, v_vec: np.ndarray,
                       mu: float) -> KeplerianElements:
    """
    Convert position/velocity state vector to Keplerian orbital elements.

    This implementation uses the angular momentum and eccentricity vector
    approach derived from first principles in the Class 1 lecture notes.

    Parameters
    ----------
    r_vec : np.ndarray
        Position vector in ECI frame [m]
    v_vec : np.ndarray
        Velocity vector in ECI frame [m/s]
    mu : float
        Gravitational parameter [m^3/s^2]

    Returns
    -------
    KeplerianElements
        Classical orbital elements with derived quantities

    Notes
    -----
    The algorithm follows these steps:
    1. Compute angular momentum h = r x v (constant for two-body motion)
    2. Compute specific energy xi = v^2/2 - mu/r (constant)
    3. Compute eccentricity vector e = (v x h)/mu - r/|r| (points to periapsis)
    4. Extract orbital elements from these vector quantities
    """
    # Magnitudes of position and velocity
    r_mag = np.linalg.norm(r_vec)
    v_mag = np.linalg.norm(v_vec)

    # ========================================================================
    # STEP 1: Angular momentum vector h = r x v
    # This is perpendicular to the orbital plane and constant in magnitude
    # ========================================================================
    h_vec = np.cross(r_vec, v_vec)
    h_mag = np.linalg.norm(h_vec)

    # ========================================================================
    # STEP 2: Node vector N = Z x h
    # Points toward the ascending node (where orbit crosses equator going north)
    # ========================================================================
    z_hat = np.array([0.0, 0.0, 1.0])  # Earth's spin axis in ECI
    n_vec = np.cross(z_hat, h_vec)
    n_mag = np.linalg.norm(n_vec)

    # ========================================================================
    # STEP 3: Eccentricity vector e = (v x h)/mu - r/|r|
    # Points toward periapsis with magnitude equal to eccentricity
    # Also known as the Laplace-Runge-Lenz vector (scaled)
    # ========================================================================
    e_vec = (np.cross(v_vec, h_vec) / mu) - (r_vec / r_mag)
    e_mag = np.linalg.norm(e_vec)

    # ========================================================================
    # STEP 4: Specific orbital energy xi = v^2/2 - mu/r
    # Negative for elliptical orbits (bound), zero for parabolic, positive for hyperbolic
    # ========================================================================
    energy = (v_mag**2 / 2.0) - (mu / r_mag)

    # ========================================================================
    # STEP 5: Semi-major axis from energy relationship a = -mu/(2*xi)
    # ========================================================================
    a = -mu / (2.0 * energy)

    # ========================================================================
    # STEP 6: Inclination - angle between h and Z-axis
    # i = arccos(h_z / |h|)
    # Range: [0, 180 deg]. Prograde if i < 90 deg, retrograde if i > 90 deg
    # ========================================================================
    inc = np.arccos(np.clip(h_vec[2] / h_mag, -1.0, 1.0))

    # ========================================================================
    # STEP 7: Right Ascension of Ascending Node (RAAN)
    # Angle from X-axis to ascending node, measured eastward in equatorial plane
    # Use atan2 for proper quadrant determination
    # ========================================================================
    if n_mag > 1e-10:  # Non-equatorial orbit
        raan = np.arctan2(n_vec[1], n_vec[0])
    else:  # Equatorial orbit: RAAN undefined, conventionally set to 0
        raan = 0.0

    # Ensure RAAN is in range [0, 2*pi)
    if raan < 0:
        raan += 2.0 * np.pi

    # ========================================================================
    # STEP 8: Argument of periapsis
    # Angle from ascending node to periapsis, measured in orbital plane
    # omega = atan2(h_hat . (N_hat x e_hat), N_hat . e_hat)
    # ========================================================================
    if n_mag > 1e-10 and e_mag > 1e-10:
        n_hat = n_vec / n_mag
        e_hat = e_vec / e_mag
        h_hat = h_vec / h_mag

        # Cosine from dot product
        cos_omega = np.dot(n_hat, e_hat)

        # Sine from triple product (determines quadrant)
        # N x e is perpendicular to orbital plane, parallel or anti-parallel to h
        sin_omega = np.dot(h_hat, np.cross(n_hat, e_hat))

        omega = np.arctan2(sin_omega, cos_omega)
    else:
        # Circular or equatorial orbit: omega undefined, set to 0
        omega = 0.0

    # Ensure omega is in range [0, 2*pi)
    if omega < 0:
        omega += 2.0 * np.pi

    # ========================================================================
    # STEP 9: True anomaly - angle from periapsis to current position
    # nu = arccos(e . r / (|e| |r|))
    # Quadrant check: if r . v < 0, satellite is approaching periapsis (nu > 180)
    # ========================================================================
    if e_mag > 1e-10:
        cos_nu = np.dot(e_vec, r_vec) / (e_mag * r_mag)
        cos_nu = np.clip(cos_nu, -1.0, 1.0)  # Numerical safety
        nu = np.arccos(cos_nu)

        # Quadrant check per Vallado Eq. 2-86
        # r . v > 0 means satellite moving away from periapsis (0 < nu < 180)
        # r . v < 0 means satellite moving toward periapsis (180 < nu < 360)
        if np.dot(r_vec, v_vec) < 0:
            nu = 2.0 * np.pi - nu
    else:
        # Circular orbit: measure from ascending node instead
        cos_nu = np.dot(n_vec, r_vec) / (n_mag * r_mag)
        nu = np.arccos(np.clip(cos_nu, -1.0, 1.0))
        if r_vec[2] < 0:
            nu = 2.0 * np.pi - nu

    # ========================================================================
    # STEP 10: Derived quantities
    # Orbital period from Kepler's third law: T = 2*pi*sqrt(a^3/mu)
    # Periapsis and apoapsis radii from trajectory equation at nu = 0, 180
    # ========================================================================
    period = 2.0 * np.pi * np.sqrt(a**3 / mu)
    r_periapsis = a * (1.0 - e_mag)
    r_apoapsis = a * (1.0 + e_mag)

    return KeplerianElements(
        a=a, e=e_mag, inc=inc, raan=raan, omega=omega, nu=nu,
        period=period, r_periapsis=r_periapsis, r_apoapsis=r_apoapsis
    )

# ============================================================================
# VERIFICATION FUNCTIONS
# ============================================================================

def verify_elements(r_vec: np.ndarray, v_vec: np.ndarray,
                    elements: KeplerianElements, mu: float) -> dict:
    """
    Verify computed elements against physical constraints and relationships.

    This provides independent checks that the conversion was performed correctly
    by testing consistency with fundamental orbital mechanics equations.

    Parameters
    ----------
    r_vec : np.ndarray
        Original position vector [m]
    v_vec : np.ndarray
        Original velocity vector [m/s]
    elements : KeplerianElements
        Computed orbital elements
    mu : float
        Gravitational parameter [m^3/s^2]

    Returns
    -------
    dict
        Dictionary of verification error magnitudes
    """
    r_mag = np.linalg.norm(r_vec)
    v_mag = np.linalg.norm(v_vec)

    checks = {}

    # Check 1: Current radius should match trajectory equation r = p/(1 + e*cos(nu))
    # where p = a(1-e^2) is the semi-latus rectum
    r_from_elements = elements.a * (1 - elements.e**2) / (1 + elements.e * np.cos(elements.nu))
    checks['radius_error_m'] = abs(r_mag - r_from_elements)

    # Check 2: Vis-viva equation: v^2 = mu(2/r - 1/a)
    # This relates velocity magnitude to position and semi-major axis
    v_expected = np.sqrt(mu * (2.0/r_mag - 1.0/elements.a))
    checks['velocity_error_m_s'] = abs(v_mag - v_expected)

    # Check 3: Angular momentum consistency: h^2 = mu * a * (1 - e^2)
    h_mag = np.linalg.norm(np.cross(r_vec, v_vec))
    h_expected = np.sqrt(mu * elements.a * (1 - elements.e**2))
    checks['angular_momentum_error'] = abs(h_mag - h_expected)

    # Check 4: Apse radii should sum to 2a (definition of semi-major axis)
    checks['apse_sum_error_m'] = abs(elements.r_periapsis + elements.r_apoapsis - 2*elements.a)

    return checks

def print_results(name: str, r_vec: np.ndarray, v_vec: np.ndarray,
                  elements: KeplerianElements, checks: dict) -> None:
    """Print formatted results for a single test case."""
    display = elements.to_degrees()

    print(f"\n{'='*70}")
    print(f"Keplerian Elements for {name}")
    print(f"{'='*70}")
    print(f"Input State Vector:")
    print(f"  r: ({r_vec[0]:16.8f}, {r_vec[1]:16.8f}, {r_vec[2]:16.8f}) m")
    print(f"  v: ({v_vec[0]:16.8f}, {v_vec[1]:16.8f}, {v_vec[2]:16.8f}) m/s")
    print()
    print(f"Computed Orbital Elements:")
    print(f"  a:    {display['a_m']:20.8f} m")
    print(f"  e:    {display['e']:20.8f}")
    print(f"  inc:  {display['inc_deg']:20.8f} deg")
    print(f"  raan: {display['raan_deg']:20.8f} deg")
    print(f"  wp:   {display['omega_deg']:20.8f} deg")
    print(f"  nu:   {display['nu_deg']:20.8f} deg")
    print()
    print(f"Derived Quantities:")
    print(f"  TP:   {display['period_s']:20.8f} sec")
    print(f"  rp:   {display['r_periapsis_m']:20.8f} m")
    print(f"  ra:   {display['r_apoapsis_m']:20.8f} m")
    print()
    print(f"Verification (errors should be ~0):")
    print(f"  Radius error:         {checks['radius_error_m']:.6e} m")
    print(f"  Velocity error:       {checks['velocity_error_m_s']:.6e} m/s")
    print(f"  Ang. momentum error:  {checks['angular_momentum_error']:.6e}")
    print(f"  Apse sum error:       {checks['apse_sum_error_m']:.6e} m")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main function to compute Keplerian elements for all homework test vectors.
    """
    # Earth's gravitational parameter (WGS84 value as specified in homework)
    MU_EARTH = 3.986004418e14  # m^3/s^2

    # Test vectors from homework (position in m, velocity in m/s)
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
    print("SPCE 5025 - HOMEWORK 1")
    print("State Vector to Keplerian Elements Conversion")
    print("=" * 70)
    print(f"\nGravitational Parameter mu = {MU_EARTH:.9e} m^3/s^2")

    for case in test_cases:
        # Compute orbital elements
        elements = state_to_keplerian(case['r'], case['v'], MU_EARTH)

        # Verify results
        checks = verify_elements(case['r'], case['v'], elements, MU_EARTH)

        # Print formatted output
        print_results(case['name'], case['r'], case['v'], elements, checks)

    print("\n" + "=" * 70)
    print("COMPUTATION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
