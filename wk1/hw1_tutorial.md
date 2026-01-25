# Homework 1: Socratic Tutorial Walkthrough

## Converting State Vectors to Keplerian Orbital Elements

This tutorial guides you through the thought process of converting a spacecraft's position and velocity (state vector) into the classical Keplerian orbital elements. Rather than presenting formulas to memorize, we'll derive each step through guided questions and physical reasoning.

---

## Phase 1: Understanding the Problem

### Guiding Questions:

1. What information fully describes an orbit in space?
2. Why might we prefer Keplerian elements over Cartesian position/velocity?
3. How many independent numbers do we need to specify a unique orbit?

*Pause and think about this before continuing.*

### Derivation and Explanation:

A spacecraft's state at any instant can be described by six numbers: three position components (x, y, z) and three velocity components (vx, vy, vz) in an inertial reference frame. However, these Cartesian coordinates change continuously as the satellite moves—they're instantaneous snapshots.

Keplerian elements offer an elegant alternative: **five parameters describe the orbit's size, shape, and orientation** (which remain constant for unperturbed two-body motion), while **one parameter (true anomaly ν) describes where the satellite is** along that fixed path.

The six classical elements are:
- **a** (semi-major axis): Determines orbit size and energy
- **e** (eccentricity): Determines orbit shape (0 = circle, 0 < e < 1 = ellipse)
- **i** (inclination): Tilt of orbital plane relative to the equator
- **Ω** (RAAN): Orientation of the orbital plane's "line of nodes"
- **ω** (argument of periapsis): Where periapsis lies within the orbital plane
- **ν** (true anomaly): Current angular position measured from periapsis

### Common Pitfall:
Students often confuse "orbital period" with one of the six elements. The period T is *derived* from a using Kepler's third law—it's not an independent element.

### Reflection:
The Keplerian elements separate the "what orbit" question (a, e, i, Ω, ω) from the "where on the orbit" question (ν). This is powerful because for an unperturbed orbit, only ν changes with time.

---

## Phase 2: Computing Angular Momentum

### Guiding Questions:

1. What physical quantity is conserved in two-body orbital motion?
2. Given r⃗ and v⃗, what vector quantity can we compute that's perpendicular to both?
3. What does the angular momentum vector tell us about the orbital plane?

*Pause and attempt to derive h⃗ = r⃗ × v⃗ before continuing.*

### Derivation and Explanation:

Starting from Newton's law for gravitational acceleration:

$$\ddot{\mathbf{r}} = -\frac{\mu}{r^3}\mathbf{r}$$

Let's cross-multiply both sides by **r**:

$$\mathbf{r} \times \ddot{\mathbf{r}} = -\frac{\mu}{r^3}(\mathbf{r} \times \mathbf{r}) = 0$$

The right side is zero because any vector crossed with itself is zero!

Now consider the time derivative of **r** × **ṙ** using the product rule:

$$\frac{d}{dt}(\mathbf{r} \times \dot{\mathbf{r}}) = \dot{\mathbf{r}} \times \dot{\mathbf{r}} + \mathbf{r} \times \ddot{\mathbf{r}} = 0 + 0 = 0$$

Both terms vanish (first because v⃗ × v⃗ = 0, second from our equation above).

**Therefore:**
$$\mathbf{h} = \mathbf{r} \times \mathbf{v} = \text{constant vector}$$

### Physical Significance:

The angular momentum vector **h** is perpendicular to both position and velocity at all times. Since both r⃗ and v⃗ lie in the orbital plane, **h** must be perpendicular to the orbital plane. Its direction is constant, meaning **the orbital plane has a fixed orientation in inertial space**.

The magnitude h = |**h**| relates directly to Kepler's second law: "equal areas swept in equal times." The areal velocity dA/dt = h/2 is constant.

### Reflection:
From **h** alone, we can determine two of our six elements (i and Ω) because **h** completely defines the orbital plane's orientation in space!

---

## Phase 3: Finding Inclination and RAAN

### Guiding Questions:

1. How do we measure the angle between two vectors mathematically?
2. The inclination is the angle between the orbital plane and the equator. What vectors define these planes?
3. Why does RAAN require `atan2` instead of just `acos`?

*Pause and sketch the geometry before continuing.*

### Derivation and Explanation:

**Inclination:**

The orbital plane is defined by its normal vector **h**. The equatorial plane is defined by the Z-axis (Earth's spin axis). The angle between these planes equals the angle between their normal vectors:

$$i = \cos^{-1}\left(\frac{\mathbf{h} \cdot \hat{\mathbf{Z}}}{|\mathbf{h}|}\right) = \cos^{-1}\left(\frac{h_z}{h}\right)$$

This naturally gives i ∈ [0°, 180°]:
- **Prograde orbits**: i < 90° (satellite moves eastward at equator crossing)
- **Polar orbits**: i ≈ 90°
- **Retrograde orbits**: i > 90° (satellite moves westward at equator crossing)

**Line of Nodes:**

The intersection of the orbital and equatorial planes forms a line called the "line of nodes." The ascending node is where the satellite crosses from the southern hemisphere to the northern hemisphere.

To find the direction to the ascending node, we need a vector that lies in both planes (i.e., perpendicular to both **h** and **Ẑ**):

$$\mathbf{N} = \hat{\mathbf{Z}} \times \mathbf{h}$$

Note that **N** automatically lies in the equatorial plane because its Z-component is zero (verify this!).

**Right Ascension of Ascending Node (RAAN):**

RAAN (Ω) is the angle from the X-axis (vernal equinox direction) to the ascending node, measured eastward in the equatorial plane:

$$\Omega = \text{atan2}(N_y, N_x)$$

### Why atan2?

We use `atan2(y, x)` instead of `acos(N_x/|N|)` because:
- `acos` only returns values in [0°, 180°]—it can't distinguish Ω = 30° from Ω = 330°
- `atan2` correctly handles all four quadrants by considering the signs of both components

After computing, ensure Ω ∈ [0°, 360°) by adding 360° if negative.

### Common Pitfall:
For equatorial orbits (i ≈ 0° or 180°), the node vector **N** becomes undefined (Z × h ≈ 0). In this case, RAAN is conventionally set to 0°.

---

## Phase 4: Energy, Semi-major Axis, and Eccentricity

### Guiding Questions:

1. What energy quantities are conserved in orbital motion?
2. What happens to potential and kinetic energy as a satellite moves from periapsis to apoapsis?
3. How does the total orbital energy relate to the orbit's size?

*Pause and consider what happens at periapsis and apoapsis specifically.*

### Derivation and Explanation:

**Specific Orbital Energy:**

Starting from the equation of motion and dot-multiplying by velocity (see lecture notes for full derivation):

$$\xi = \frac{v^2}{2} - \frac{\mu}{r} = \text{constant}$$

This is kinetic energy plus gravitational potential energy, per unit mass. The key insight:
- **Elliptical (bound) orbits**: ξ < 0
- **Parabolic orbits**: ξ = 0 (escape trajectory)
- **Hyperbolic orbits**: ξ > 0

**Semi-major Axis from Energy:**

By evaluating energy at periapsis (where velocity and position are perpendicular, so we can use simple geometry), we derive:

$$\xi = -\frac{\mu}{2a} \quad \Rightarrow \quad a = -\frac{\mu}{2\xi}$$

This is remarkable: **the semi-major axis depends only on total energy**, not on angular momentum or eccentricity!

**The Eccentricity Vector:**

The lecture notes derive that the vector:

$$\mathbf{B} = \dot{\mathbf{r}} \times \mathbf{h} - \mu\frac{\mathbf{r}}{r}$$

is constant and **points toward periapsis**. The eccentricity is simply:

$$e = \frac{|\mathbf{B}|}{\mu}$$

Alternatively, eccentricity can be found from angular momentum and energy:

$$e = \sqrt{1 + \frac{2h^2\xi}{\mu^2}}$$

Both methods should give identical results—use this as a verification check!

### Reflection:
The eccentricity vector **B** (or equivalently **e** = **B**/μ) is particularly powerful because:
1. Its magnitude gives eccentricity directly
2. Its direction points to periapsis, enabling us to find ω and ν

---

## Phase 5: Argument of Periapsis

### Guiding Questions:

1. How do we measure an angle that lies *within* the orbital plane, not in a reference coordinate plane?
2. Why is ω measured specifically from the ascending node rather than some other reference?
3. How do we determine if ω is in the first half (0-180°) or second half (180-360°) of its range?

*Pause and visualize the geometry in 3D before continuing.*

### Derivation and Explanation:

The argument of periapsis ω is the angle from the ascending node **N** to the eccentricity vector **e** (which points at periapsis), measured in the orbital plane in the direction of satellite motion.

We need both sine and cosine for unambiguous quadrant determination.

**Cosine** from the dot product of unit vectors:

$$\cos\omega = \hat{\mathbf{N}} \cdot \hat{\mathbf{e}}$$

**Sine** requires more thought. The cross product **N̂** × **ê** produces a vector perpendicular to the orbital plane—either parallel to **h** (if ω < 180°) or anti-parallel to **h** (if ω > 180°). We extract the sign by projecting onto **h**:

$$\sin\omega = \hat{\mathbf{h}} \cdot (\hat{\mathbf{N}} \times \hat{\mathbf{e}})$$

Finally:

$$\omega = \text{atan2}(\sin\omega, \cos\omega)$$

Adjust to [0°, 360°) if negative.

### Common Pitfall:
- **Equatorial orbits** (i ≈ 0°): **N** is undefined, so ω is undefined. Use "longitude of periapsis" ϖ = Ω + ω instead.
- **Circular orbits** (e ≈ 0): Periapsis doesn't exist! Use "argument of latitude" u = ω + ν instead.

---

## Phase 6: True Anomaly and the Quadrant Check

### Guiding Questions:

1. The true anomaly comes from a dot product giving cos(ν). How do we know which "side" of periapsis the satellite is on?
2. What physical quantity changes sign exactly at periapsis and apoapsis?
3. Can you think of a simple check using the given position and velocity?

*Pause and think about what r⃗ · v⃗ represents physically.*

### Derivation and Explanation:

**Basic Formula:**

True anomaly ν is the angle from periapsis (direction of **e**) to the current position:

$$\cos\nu = \frac{\mathbf{e} \cdot \mathbf{r}}{|\mathbf{e}| \cdot |\mathbf{r}|}$$

However, `acos` only returns values in [0°, 180°]. If ν is actually between 180° and 360°, we'll get the wrong answer!

**The Key Insight:**

Consider the radial velocity component: $v_r = \frac{\mathbf{r} \cdot \mathbf{v}}{r}$

This is the rate at which the satellite is moving toward or away from Earth's center:
- **Satellite moving away from periapsis** (0° < ν < 180°): The radius is increasing, so vr > 0, meaning **r⃗ · v⃗ > 0**
- **Satellite moving toward periapsis** (180° < ν < 360°): The radius is decreasing, so vr < 0, meaning **r⃗ · v⃗ < 0**

**The Quadrant Rule (Vallado Equation 2-86):**

```
1. Compute ν = acos(e⃗ · r⃗ / (e × r))     [This gives ν ∈ [0°, 180°]]
2. If r⃗ · v⃗ < 0, then ν = 360° - ν       [Corrects to proper quadrant]
```

### Physical Interpretation:

At periapsis (ν = 0°) and apoapsis (ν = 180°), the velocity is purely tangential, so r⃗ · v⃗ = 0 exactly. These are the boundaries between "outbound" and "inbound" motion.

### Reflection:
This elegant check works because there's a one-to-one correspondence between the sign of radial velocity and whether ν is in [0°, 180°] or [180°, 360°].

---

## Phase 7: Period and Apse Distances

### Guiding Questions:

1. How does Kepler's third law emerge from the derivations we've done?
2. What is the physical meaning of having rp ≈ ra for a near-circular orbit?
3. How can we verify our computed elements are self-consistent?

*Pause and verify the period formula dimensionally.*

### Derivation and Explanation:

**Orbital Period:**

From the constant areal velocity (h/2) and the total area of an ellipse (πab):

$$T = \frac{2\pi a b}{h}$$

Using the relationship $b = a\sqrt{1-e^2}$ (from ellipse geometry) and $h = \sqrt{\mu a(1-e^2)}$ (from angular momentum):

$$T = 2\pi\sqrt{\frac{a^3}{\mu}}$$

This is **Kepler's Third Law**! Notice that the period depends *only* on the semi-major axis—eccentricity doesn't matter.

**Dimensional Check:**

$$[T] = \sqrt{\frac{[a]^3}{[\mu]}} = \sqrt{\frac{m^3}{m^3/s^2}} = \sqrt{s^2} = s \quad \checkmark$$

**Apse Distances:**

From the trajectory equation $r = \frac{a(1-e^2)}{1+e\cos\nu}$ at the special points:

At periapsis (ν = 0°):
$$r_p = \frac{a(1-e^2)}{1+e} = a(1-e)$$

At apoapsis (ν = 180°):
$$r_a = \frac{a(1-e^2)}{1-e} = a(1+e)$$

**Verification Checks:**

We can verify our solution with several independent checks:
1. $r_p + r_a = 2a$ (definition of semi-major axis)
2. Current radius matches trajectory equation
3. Vis-viva equation: $v^2 = \mu\left(\frac{2}{r} - \frac{1}{a}\right)$
4. Angular momentum: $h^2 = \mu a(1-e^2)$

---

## Summary

### Overall Solution Strategy:

1. **Compute h⃗ = r⃗ × v⃗** (conserved angular momentum)
2. **Compute ξ = v²/2 - μ/r** (conserved specific energy)
3. **Compute e⃗ = (v⃗ × h⃗)/μ - r⃗/r** (eccentricity vector pointing to periapsis)
4. **Extract a from ξ**: a = -μ/(2ξ)
5. **Extract e from |e⃗|**: e = |e⃗|
6. **Extract i, Ω from h⃗ direction**: inclination and RAAN
7. **Extract ω from angle between N⃗ and e⃗**: argument of periapsis
8. **Extract ν from angle between e⃗ and r⃗**: true anomaly with quadrant check
9. **Derive T, rp, ra from a and e**: period and apse distances

### Key Guiding Questions to Remember:

- What is conserved in two-body motion? (h⃗, ξ, and e⃗ direction)
- How do we get unambiguous angles? (Use atan2 with both sin and cos)
- How do we check our answer? (Vis-viva, trajectory equation, apse sum)

### Practice Extensions:

1. **Reverse Problem**: Implement Keplerian elements → state vector conversion
2. **Singular Cases**: Handle circular orbits (e ≈ 0) and equatorial orbits (i ≈ 0) with alternative element sets
3. **Time Propagation**: Given ν at time t₀, find ν at time t using Kepler's equation
4. **Physical Intuition**: Compute elements for known satellites (ISS: i ≈ 51.6°, GPS: T ≈ 12 hr, GEO: T ≈ 24 hr) and verify against published data
