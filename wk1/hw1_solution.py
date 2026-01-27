"""
Keplerian Orbital Elements from State Vectors
SPCE 5025 - Fundamentals of Astronautics - Homework 1

Takes an Earth-Centered Inertial (ECI) position/velocity state vector and
converts it to the classical Keplerian orbital elements. The approach here
relies on angular momentum and the eccentricity vector — both of which stay
constant in two-body motion, which makes them ideal for extracting orbit geometry.

Author: Jordan Clayton
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class KeplerianElements:
    """Holds the six classical orbital elements plus a few useful derived quantities."""
    a: float       # Semi-major axis [m]
    e: float       # Eccentricity — 0 is circular, closer to 1 means more elongated
    inc: float     # Inclination [rad]
    raan: float    # Right Ascension of Ascending Node [rad]
    omega: float   # Argument of periapsis [rad]
    nu: float      # True anomaly — where we are on the orbit right now [rad]
    period: float  # Orbital period [s]
    r_periapsis: float  # Closest approach to Earth [m]
    r_apoapsis: float   # Farthest point from Earth [m]

    def to_degrees(self) -> dict:
        """Converts angular elements to degrees — easier to read and sanity-check."""
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
    Convert a position/velocity state vector into Keplerian orbital elements.

    I'm using the angular momentum and eccentricity vector approach from the
    Class 1 lecture notes. It's a pretty standard method — the nice thing is
    that both h and e are conserved in two-body motion, so they give us direct
    access to the orbit's shape and orientation.

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
    The basic game plan:
    1. Compute angular momentum h = r x v (stays constant for two-body motion)
    2. Compute specific energy xi = v^2/2 - mu/r (also constant)
    3. Compute eccentricity vector e = (v x h)/mu - r/|r| (points at periapsis)
    4. Extract the orbital elements from these vectors
    """
    # Magnitudes of position and velocity
    r_mag = np.linalg.norm(r_vec)
    v_mag = np.linalg.norm(v_vec)

    # ========================================================================
    # STEP 1: Angular momentum vector h = r x v
    # This guy is perpendicular to the orbital plane and — crucially — stays
    # constant in magnitude. It's our key to finding inclination and RAAN.
    # ========================================================================
    h_vec = np.cross(r_vec, v_vec)
    h_mag = np.linalg.norm(h_vec)

    # ========================================================================
    # STEP 2: Node vector N = Z x h
    # Points toward the ascending node, i.e., where the orbit crosses the
    # equator heading north. We'll need this for RAAN and argument of periapsis.
    # ========================================================================
    z_hat = np.array([0.0, 0.0, 1.0])  # Earth's spin axis in ECI
    n_vec = np.cross(z_hat, h_vec)
    n_mag = np.linalg.norm(n_vec)

    # ========================================================================
    # STEP 3: Eccentricity vector e = (v x h)/mu - r/|r|
    # This is essentially the Laplace-Runge-Lenz vector scaled by mu. It points
    # straight at periapsis, and its magnitude gives us the eccentricity directly.
    # ========================================================================
    e_vec = (np.cross(v_vec, h_vec) / mu) - (r_vec / r_mag)
    e_mag = np.linalg.norm(e_vec)

    # ========================================================================
    # STEP 4: Specific orbital energy xi = v^2/2 - mu/r
    # If this is negative, we've got a bound (elliptical) orbit. Zero means
    # parabolic escape, positive means hyperbolic. For Earth satellites, it's negative.
    # ========================================================================
    energy = (v_mag**2 / 2.0) - (mu / r_mag)

    # ========================================================================
    # STEP 5: Semi-major axis from energy: a = -mu/(2*xi)
    # The energy-semimajor axis relationship is one of the cleanest in orbital
    # mechanics — energy depends only on 'a', not on eccentricity.
    # ========================================================================
    a = -mu / (2.0 * energy)

    # ========================================================================
    # STEP 6: Inclination — angle between h and the Z-axis
    # i = arccos(h_z / |h|)
    # Ranges from 0 to 180 deg. Below 90 deg is prograde (satellite moves
    # eastward at equator), above 90 deg is retrograde.
    # ========================================================================
    inc = np.arccos(np.clip(h_vec[2] / h_mag, -1.0, 1.0))

    # ========================================================================
    # STEP 7: Right Ascension of Ascending Node (RAAN)
    # This is the angle from the X-axis (vernal equinox) to the ascending node,
    # measured eastward in the equatorial plane. Using atan2 here handles the
    # quadrant automatically — way better than acos for this.
    # ========================================================================
    if n_mag > 1e-10:  # Normal case: non-equatorial orbit
        raan = np.arctan2(n_vec[1], n_vec[0])
    else:  # Equatorial orbit: RAAN isn't really defined, so we just set it to 0
        raan = 0.0

    # Make sure RAAN lands in [0, 2*pi)
    if raan < 0:
        raan += 2.0 * np.pi

    # ========================================================================
    # STEP 8: Argument of periapsis
    # Angle from the ascending node to periapsis, measured in the orbital plane.
    # We need both sine and cosine to get the right quadrant.
    # ========================================================================
    if n_mag > 1e-10 and e_mag > 1e-10:
        n_hat = n_vec / n_mag
        e_hat = e_vec / e_mag
        h_hat = h_vec / h_mag

        # Cosine comes from the dot product
        cos_omega = np.dot(n_hat, e_hat)

        # For sine, we use the triple product — N x e gives a vector that's
        # either parallel or anti-parallel to h, telling us which side we're on
        sin_omega = np.dot(h_hat, np.cross(n_hat, e_hat))

        omega = np.arctan2(sin_omega, cos_omega)
    else:
        # Circular or equatorial orbit: omega isn't well-defined, default to 0
        omega = 0.0

    # Keep omega in [0, 2*pi)
    if omega < 0:
        omega += 2.0 * np.pi

    # ========================================================================
    # STEP 9: True anomaly — angle from periapsis to current position
    # nu = arccos(e . r / (|e| |r|))
    # The tricky part: acos only gives 0-180 deg, so we need a quadrant check.
    # ========================================================================
    if e_mag > 1e-10:
        cos_nu = np.dot(e_vec, r_vec) / (e_mag * r_mag)
        cos_nu = np.clip(cos_nu, -1.0, 1.0)  # Clamp for numerical safety
        nu = np.arccos(cos_nu)

        # Quadrant check (Vallado Eq. 2-86): if r·v < 0, the satellite is
        # heading toward periapsis, meaning nu should be in (180, 360) deg
        if np.dot(r_vec, v_vec) < 0:
            nu = 2.0 * np.pi - nu
    else:
        # Circular orbit: no periapsis to measure from, so use ascending node
        cos_nu = np.dot(n_vec, r_vec) / (n_mag * r_mag)
        nu = np.arccos(np.clip(cos_nu, -1.0, 1.0))
        if r_vec[2] < 0:
            nu = 2.0 * np.pi - nu

    # ========================================================================
    # STEP 10: Derived quantities
    # Period comes from Kepler's third law: T = 2*pi*sqrt(a^3/mu)
    # Periapsis and apoapsis radii are just the trajectory equation at nu = 0, 180
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
    Sanity-check the computed elements against known physical relationships.

    This is basically a self-test — if we did the conversion right, these
    independent checks should all come out to ~zero (within floating-point noise).
    It's a good habit to verify results against fundamental equations.

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

    # Check 1: Does the current radius match what the trajectory equation predicts?
    # r = p/(1 + e*cos(nu)), where p = a(1-e^2) is the semi-latus rectum
    r_from_elements = elements.a * (1 - elements.e**2) / (1 + elements.e * np.cos(elements.nu))
    checks['radius_error_m'] = abs(r_mag - r_from_elements)

    # Check 2: Vis-viva equation — this one's a classic: v^2 = mu(2/r - 1/a)
    # If our 'a' is correct, we should get back the same velocity magnitude
    v_expected = np.sqrt(mu * (2.0/r_mag - 1.0/elements.a))
    checks['velocity_error_m_s'] = abs(v_mag - v_expected)

    # Check 3: Angular momentum should satisfy h^2 = mu * a * (1 - e^2)
    h_mag = np.linalg.norm(np.cross(r_vec, v_vec))
    h_expected = np.sqrt(mu * elements.a * (1 - elements.e**2))
    checks['angular_momentum_error'] = abs(h_mag - h_expected)

    # Check 4: Periapsis + apoapsis should equal 2a (that's the definition)
    checks['apse_sum_error_m'] = abs(elements.r_periapsis + elements.r_apoapsis - 2*elements.a)

    return checks

def print_results(name: str, r_vec: np.ndarray, v_vec: np.ndarray,
                  elements: KeplerianElements, checks: dict) -> None:
    """Print formatted results for a single test case to console."""
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


def write_results_to_file(filename: str, test_cases: list,
                          all_elements: list, mu: float) -> None:
    """
    Dump results to a text file — formatted to match what the professor expects.

    This makes it easy to submit or compare against the provided solution.

    Parameters
    ----------
    filename : str
        Where to save the output
    test_cases : list
        List of test case dictionaries with 'name', 'r', 'v' keys
    all_elements : list
        Corresponding KeplerianElements for each test case
    mu : float
        Gravitational parameter we used
    """
    with open(filename, 'w') as fid:
        fid.write("Homework 1 Results\n")
        fid.write("=" * 60 + "\n")
        fid.write(f"mu: {mu:.9e} m^3/s^2\n\n")

        for case, elements in zip(test_cases, all_elements):
            r = case['r']
            v = case['v']
            display = elements.to_degrees()

            # Input vectors
            fid.write(f"{case['name']}\n")
            fid.write(f"r:  ( {r[0]:16.8f}, {r[1]:16.8f}, {r[2]:16.8f}) m\n")
            fid.write(f"rd: ( {v[0]:16.8f}, {v[1]:16.8f}, {v[2]:16.8f}) m/sec\n\n")

            # Computed elements — trying to match the professor's formatting
            fid.write(f"Keplerian Elements for {case['name']}\n")
            fid.write(f"        a:    {display['a_m']:16.8f} m\n")
            fid.write(f"        e:    {display['e']:16.8f}\n")
            fid.write(f"        inc:  {display['inc_deg']:16.8f} deg\n")
            fid.write(f"        raan: {display['raan_deg']:16.8f} deg\n")
            fid.write(f"        wp:   {display['omega_deg']:16.8f} deg\n")
            fid.write(f"        nu:   {display['nu_deg']:16.8f} deg\n")
            fid.write(f"        TP:   {display['period_s']:16.8f} sec\n")
            fid.write(f"        rp:   {display['r_periapsis_m']:16.8f} m\n")
            fid.write(f"        ra:   {display['r_apoapsis_m']:16.8f} m\n")
            fid.write("\n\n")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Run through all four homework test vectors and compute their orbital elements.
    Results go to both the console and a text file for easy submission.
    """
    import os

    # Earth's gravitational parameter — using the WGS84 value given in the homework
    MU_EARTH = 3.986004418e14  # m^3/s^2

    # The four state vectors we need to convert (all in meters and m/s)
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

    # We'll collect all results here so we can write them to a file at the end
    all_elements = []

    for case in test_cases:
        # Do the actual conversion
        elements = state_to_keplerian(case['r'], case['v'], MU_EARTH)
        all_elements.append(elements)

        # Run verification checks — these should all be basically zero
        checks = verify_elements(case['r'], case['v'], elements, MU_EARTH)

        # Show results in the console
        print_results(case['name'], case['r'], case['v'], elements, checks)

    # Also save to a text file for submission
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "hw1_results.txt")
    write_results_to_file(output_file, test_cases, all_elements, MU_EARTH)

    print("\n" + "=" * 70)
    print("COMPUTATION COMPLETE")
    print("=" * 70)
    print(f"\nResults also written to: {output_file}")

if __name__ == "__main__":
    main()
