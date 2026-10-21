"""
taster_helpers.py
=================
Data, checks and plots for the lap sim hands-on notebook (lapsim_handson.ipynb).

The checks compare your functions with reference answers for the same simple
model, using the car numbers given in the notebook. Peeking is allowed.
"""

from __future__ import annotations

import csv
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REAL_LAP_TIME = 57.45   # s, the OUR lap time simulation on the same track

# The car, as in the notebook. The checks use these values.
m, g = 360.0, 9.81                 # kg, m/s²
mu = 1.54                          # tyre grip
rho, A = 1.162, 0.72               # kg/m³, m²
CL, CD = 2.0, 1.0                  # downforce and drag coefficients
P, eta = 80e3, 0.92                # W (FS rules), drivetrain efficiency
T, G, r = 255.0, 3.58, 0.2032      # Nm, gear ratio, m tyre radius
h, L = 0.20, 1.62                  # m CoG height, m wheelbase


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

def _read(name):
    path = name if os.path.exists(name) else os.path.join(HERE, name)
    with open(path, newline="") as fh:
        rows = list(csv.reader(fh))[1:]
    return np.array(rows, dtype=float).T


def load_track():
    """The FSUK 2026 course: distance s, position x and y, curvature (1/m), slice length ds."""
    s, x, y, kappa = _read("track_fsuk26.csv")
    return s, x, y, kappa, float(s[1] - s[0])


def load_real_lap():
    """Our real lap sim on the same track: distance (m) and speed (m/s)."""
    s, v_kmh, _ = _read("real_lap.csv")
    return s, v_kmh / 3.6


# ---------------------------------------------------------------------------
# Reference answers
# ---------------------------------------------------------------------------

def _downforce(v): return 0.5 * rho * CL * A * v**2
def _drag(v): return 0.5 * rho * CD * A * v**2
def _max_lateral(v): return mu * (m * g + _downforce(v)) / m


def _corner_speed(kappa):
    k = abs(kappa)
    if k < 1e-9:
        return np.inf
    den = m * k - mu * 0.5 * rho * CL * A
    return np.inf if den <= 0 else np.sqrt(mu * m * g / den)


def _max_accel(v):
    v = max(v, 0.5)
    F_tyres = mu * 0.5 * (m * g + _downforce(v))
    F_motor = T * G * eta / r
    F_power = P * eta / v
    return (min(F_tyres, F_motor, F_power) - _drag(v)) / m


def _max_brake(v): return (mu * (m * g + _downforce(v)) + _drag(v)) / m


def _grip_share(v, kappa):
    return np.sqrt(max(0.0, 1.0 - (v**2 * abs(kappa) / _max_lateral(v)) ** 2))


def _backward(v_cap, kappa, ds, max_brake, grip_share):
    v = np.zeros(len(v_cap))
    v[-1] = min(v_cap[-1], 100.0)
    for i in range(len(v_cap) - 1, 0, -1):
        a = max_brake(v[i]) * grip_share(v[i], kappa[i])
        v[i - 1] = min(np.sqrt(v[i] ** 2 + 2 * a * ds), v_cap[i - 1])
    return v


def _lap_time(v, ds): return float(np.sum(ds / ((v[:-1] + v[1:]) / 2)))


def _max_accel_transfer(v):
    v = max(v, 0.5)
    a_tyres = (mu * 0.5 * (m * g + _downforce(v)) - _drag(v)) / (m - mu * m * h / L)
    a_other = (min(T * G * eta / r, P * eta / v) - _drag(v)) / m
    return min(a_tyres, a_other)


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def _close(a, b, tol):
    if np.isinf(b):
        return a is not None and (np.isinf(a) or a > 1e3)
    return a is not None and abs(a - b) <= tol * max(1.0, abs(b))


def _run(fn, *args):
    try:
        out = fn(*args)
        return None if out is None or out is Ellipsis else float(out)   # not written yet
    except Exception as e:   # show the error, not a traceback
        print(f"  {type(e).__name__}: {e}")
        return None


def _report(name, cases, hint):
    ok = True
    for label, got, want, tol in cases:
        good = _close(got, want, tol)
        ok &= good
        shown = "nothing yet" if got is None else f"{got:.3f}"
        print(f"  {'✓' if good else '✗'} {label}: got {shown}, expected {want:.3f}")
    print(f"{'PASS' if ok else 'Not yet'}: {name}" + ("" if ok else f"\n  Hint: {hint}"))
    return ok


def check_aero(downforce, drag):
    cases = [(f"downforce({v})", _run(downforce, v), _downforce(v), 1e-3) for v in (10, 25)]
    cases += [(f"drag({v})", _run(drag, v), _drag(v), 1e-3) for v in (10, 25)]
    return _report("downforce and drag", cases, "F = ½·ρ·C·A·v², with C = CL for downforce and CD for drag.")


def check_max_lateral(max_lateral):
    cases = [(f"max_lateral({v})", _run(max_lateral, v), _max_lateral(v), 1e-3) for v in (0, 20, 30)]
    return _report("max_lateral", cases, "The tyres can give μ × (load). The load is the weight m·g plus the downforce. Divide by m for an acceleration.")


def check_corner_speed(corner_speed):
    cases = [(f"corner_speed({k})", _run(corner_speed, k), _corner_speed(k), 1e-3) for k in (0.1, 0.05, -0.05, 0.02, 0.001, 0.0)]
    return _report("corner_speed", cases, "Solve v²·κ = μ·(m·g + k·v²)/m for v, with k = ½·ρ·CL·A. If the bottom of your fraction is ≤ 0, the bend sets no limit: return np.inf. Use abs(kappa): left and right bends are the same.")


def check_max_accel(max_accel):
    cases = [(f"max_accel({v})", _run(max_accel, v), _max_accel(v), 2e-3) for v in (1, 10, 25, 35)]
    return _report("max_accel", cases, "Three forces: the rear tyres (half the load × μ), the motor (T·G·η/r) and the power limit (P·η/v). Take the smallest, subtract drag, divide by m.")


def check_max_brake(max_brake):
    cases = [(f"max_brake({v})", _run(max_brake, v), _max_brake(v), 1e-3) for v in (0, 20, 35)]
    return _report("max_brake", cases, "All four tyres brake: μ × (m·g + downforce). Drag helps you slow down, so add it. Divide by m, and keep it positive.")


def check_backward(backward_pass, v_cap, kappa, ds, max_brake, grip_share):
    try:
        got = np.asarray(backward_pass(v_cap), dtype=float)
    except Exception as e:
        print(f"  {type(e).__name__}: {e}")
        got = None
    want = _backward(v_cap, kappa, ds, max_brake, grip_share)
    ok = got is not None and got.shape == want.shape and np.allclose(got, want, atol=0.01)
    if ok:
        print("PASS: backward_pass")
    else:
        if got is not None and got.shape == want.shape:
            i = int(np.argmax(np.abs(got - want)))
            print(f"  ✗ biggest difference at slice {i}: got {got[i]:.2f} m/s, expected {want[i]:.2f} m/s")
        print("Not yet: backward_pass\n  Hint: copy the three lines of forward_pass. Walk from i to i-1, use max_brake "
              "instead of max_accel, and cap with v_cap[i - 1].")
    return ok


def check_lap_time(lap_time, ds):
    v = np.array([0.0, 10.0, 20.0, 20.0, 10.0])
    return _report("lap_time", [("lap_time([0, 10, 20, 20, 10])", _run(lap_time, v), _lap_time(v, ds), 1e-6)],
                   "Each slice takes ds ÷ (its average speed). The average over a slice is (v[i] + v[i+1]) / 2. Add them all up.")


def check_grip_share(grip_share):
    cases = [(f"grip_share({v}, {k})", _run(grip_share, v, k), _grip_share(v, k), 1e-3) for v, k in ((20, 0.0), (20, 0.02), (15, 0.06), (20, 0.05))]
    return _report("grip_share", cases, "Grip used sideways = v²·|κ|. As a fraction f of max_lateral(v), what is left for accelerating or braking is √(1 − f²). Never below 0.")


def check_max_accel_transfer(fn):
    cases = [(f"max_accel_with_transfer({v})", _run(fn, v), _max_accel_transfer(v), 2e-3) for v in (5, 15, 25)]
    return _report("max_accel_with_transfer", cases, "With a = (F_tyres − drag)/m and F_tyres = μ·(½(m·g + downforce) + m·a·h/L), a is on both sides. Collect the a terms and solve.")


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

def show_track(s, x, y, kappa):
    import matplotlib.pyplot as plt
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4), gridspec_kw={"width_ratios": [1, 2.4]})
    sc = a1.scatter(x, y, c=np.abs(kappa), s=4, cmap="viridis_r", vmax=0.15)
    a1.plot(x[0], y[0], "k|", ms=14); a1.set_aspect("equal"); a1.set_title("FSUK 2026 course"); a1.axis("off")
    fig.colorbar(sc, ax=a1, label="curvature |κ| (1/m)", shrink=0.8)
    a2.plot(s, np.abs(kappa), color="#5f6368", lw=1)
    a2.set_xlabel("distance (m)"); a2.set_ylabel("|κ| (1/m)"); a2.set_title("How tight each slice is (1/κ = bend radius)")
    a2.grid(alpha=0.3); plt.tight_layout(); plt.show()


def show_lap(s, v_cap=None, v_fwd=None, v_bwd=None, v_lap=None, zoom=None):
    """Your speed profile against the real lap sim. zoom=(start_m, end_m) to look closer."""
    import matplotlib.pyplot as plt
    s_real, v_real = load_real_lap()
    fig, ax = plt.subplots(figsize=(11, 3.6))
    kmh = lambda v: np.where(np.isfinite(v), np.asarray(v) * 3.6, np.nan)
    if v_cap is not None:
        ax.fill_between(s, kmh(np.minimum(v_cap, 60)), 130, color="#9aa0a6", alpha=0.25, lw=0, label="too fast for the bend")
    if v_fwd is not None: ax.plot(s, kmh(v_fwd), color="#1e8e3e", lw=1.2, alpha=0.8, label="forward pass")
    if v_bwd is not None: ax.plot(s, kmh(v_bwd), color="#d93025", lw=1.2, alpha=0.8, label="backward pass")
    ax.plot(s_real, v_real * 3.6, color="#9aa0a6", lw=1.5, ls="--", label="our real lap sim")
    if v_lap is not None: ax.plot(s, kmh(v_lap), color="#e8710a", lw=2.2, label="your lap")
    ax.set_ylim(0, 120); ax.set_xlim(*(zoom or (0, s[-1])))
    ax.set_xlabel("distance (m)"); ax.set_ylabel("speed (km/h)"); ax.grid(alpha=0.3); ax.legend(loc="lower right", fontsize=8, ncol=3)
    plt.tight_layout(); plt.show()


def compare(t):
    d = t - REAL_LAP_TIME
    print(f"Your lap: {t:.2f} s    our real lap sim: {REAL_LAP_TIME:.2f} s    difference: {d:+.2f} s ({100 * d / REAL_LAP_TIME:+.1f}%)")
