"""Build lapsim_handson.ipynb, then run every cell in order as a test.

Edit the cells below, then, from the repo root:

    python notebook/build_notebook.py notebook/lapsim_handson.ipynb

The test runs each TODO cell as a student would leave it (its check must say
"Not yet", not crash), then the solution under it (its check must PASS), and
prints the lap times. Commit the .ipynb it writes.
"""
import io, json, os, sys, contextlib

OUT = sys.argv[1]
cells = []


def md(text):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": text.strip("\n")})


def code(text, hidden_title=None):
    src = text.strip("\n")
    meta = {}
    if hidden_title:
        src = f'# @title {hidden_title} {{ display-mode: "form" }}\n' + src
        # Colab shows a form cell as its title only; Jupyter and VS Code fold its code with source_hidden.
        meta = {"cellView": "form", "jupyter": {"source_hidden": True}}
    cells.append({"cell_type": "code", "metadata": meta, "execution_count": None, "outputs": [], "source": src})


def solution(n, text):
    code(text, f"Solution {n} (open it if you are stuck, then run it)")


md("""
# Build your own lap time simulation

In 15 minutes you will write the heart of a lap time simulation: part of the **model of the car**, and the **algorithm** that turns it into a lap time on a real track. Then you compare yours with the one the OUR simulation team uses.

**How it works**
- Run each cell with ▶ (or Shift + Enter), from top to bottom. Please do not use *Run all*.
- Cells marked **TODO** are yours: replace each `...` with code. There are four.
- The cell under each TODO checks your answer and gives a hint if it is not right yet.
- Stuck? Open the *Solution* cell under it, run it, and carry on.

The interactive version of everything here: [OUR Lap Sim Taster](https://anjunming1202.github.io/lapsim-taster/)
""")
code("""
import os, urllib.request
import numpy as np
BASE = "https://raw.githubusercontent.com/anjunming1202/lapsim-taster/main/notebook/"
for f in ["taster_helpers.py", "track_fsuk26.csv", "real_lap.csv"]:
    if not os.path.exists(f):
        urllib.request.urlretrieve(BASE + f, f)
from taster_helpers import *
s, x, y, kappa, ds = load_track()
print(f"Track: {s[-1]:.0f} m in {len(s)} slices of {ds:.0f} m")
show_track(s, x, y, kappa)
""", "Setup: run me first")

md("""
## 1. The car model

A lap sim is two things: a **model** of what the car can do, and an **algorithm** that applies it to every slice of track. The track is a list of 1 m slices, each with a curvature κ = 1 / (bend radius).

Most of the model is written for you. Read it: every line is one piece of physics. Units are SI (m, s, kg, N); speeds are in m/s.
""")
code("""
m, g = 360.0, 9.81                 # mass with driver (kg), gravity (m/s²)
mu = 1.54                          # tyre grip: a tyre gives at most μ × the load on it
rho, A = 1.162, 0.72               # air density (kg/m³), reference area (m²)
CL, CD = 2.0, 1.0                  # downforce and drag coefficients
P, eta = 80e3, 0.92                # power limit (W, FS rules), drivetrain efficiency
T, G, r = 255.0, 3.58, 0.2032      # motor torque (Nm), gear ratio, tyre radius (m)

def downforce(v):                  # the wings push the car down, more at speed: ½ρ·CL·A·v²
    return 0.5 * rho * CL * A * v**2

def drag(v):                       # the air holds the car back: ½ρ·CD·A·v²
    return 0.5 * rho * CD * A * v**2

def max_lateral(v):                # hardest the car can turn: μ × (weight + downforce) / m
    return mu * (m * g + downforce(v)) / m

def corner_speed(kappa):           # fastest through a bend: solve v²·κ = max_lateral(v) for v
    bottom = m * abs(kappa) - mu * 0.5 * rho * CL * A
    return np.inf if bottom <= 0 else np.sqrt(mu * m * g / bottom)   # gentle bend: no limit

def max_brake(v):                  # hardest the car can brake: four tyres, and drag helps
    return (mu * (m * g + downforce(v)) + drag(v)) / m
""")

md("""
### Exercise 1: how hard can the car accelerate?

Three things limit it, and the car gets whichever is **smallest**:
- **the rear tyres**: only the rear wheels drive, and they carry half the load: $\\mu \\cdot \\tfrac{1}{2}(m g + \\text{downforce})$
- **the motor**: torque $T$ through the gearbox onto a wheel of radius $r$: $T\\,G\\,\\eta / r$
- **the power limit**: power = force × speed, so the force is $P\\,\\eta / v$

Then drag pulls back. Turn the force into an acceleration by dividing by $m$.
""")
code("""
def max_accel(v):
    v = max(v, 0.5)     # so the power limit never divides by zero at the start
    ...                 # TODO: return the largest forward acceleration (m/s²) at speed v
""")
code("check_max_accel(max_accel)")
solution("1", """
def max_accel(v):
    v = max(v, 0.5)
    F_tyres = mu * 0.5 * (m * g + downforce(v))
    F_motor = T * G * eta / r
    F_power = P * eta / v
    return (min(F_tyres, F_motor, F_power) - drag(v)) / m

check_max_accel(max_accel)
""")

md("""
## 2. The algorithm

**Corner limits.** In each slice the car can go no faster than the bend allows (grey: too fast).

**The forward pass.** Start from rest and accelerate as hard as possible, slice by slice, never faster than a bend allows. Over one slice of length `ds`: $v_{next}^2 = v^2 + 2\\,a\\,ds$. Read the three lines inside the loop.

(Ignore `grip_share` for now: it is always 1. You will improve it in exercise 4.)
""")
code("""
v_cap = np.array([corner_speed(k) for k in kappa])

def grip_share(v, kappa):
    return 1.0          # how much grip is left for accelerating or braking (exercise 4)

def forward_pass(v_cap):
    v = np.zeros(len(s))                                   # start from rest
    for i in range(len(s) - 1):
        a = max_accel(v[i]) * grip_share(v[i], kappa[i])   # how hard can we accelerate here?
        v_next = np.sqrt(v[i]**2 + 2 * a * ds)             # v² = u² + 2·a·s over one slice
        v[i + 1] = min(v_next, v_cap[i + 1])               # never faster than the next bend allows
    return v

v_fwd = forward_pass(v_cap)
show_lap(s, v_cap=v_cap, v_fwd=v_fwd)
""")
md("At every bend the green line drops **straight down**: that would mean stopping instantly, which no car can do. Next, braking.")

md("""
### Exercise 2: the backward pass

Braking has to start **before** a bend. So work **backwards** from the finish: walk from the last slice to the first, and at each step ask *"what is the fastest I could be here and still brake down to the speed of the slice after it?"*

It is the forward pass in a mirror. Three lines, like the ones above, but:
- go from slice `i` to slice `i - 1`;
- use `max_brake` instead of `max_accel`;
- cap with `v_cap[i - 1]`.
""")
code("""
def backward_pass(v_cap):
    v = np.zeros(len(s))
    v[-1] = min(v_cap[-1], 100.0)            # the finish line sets no limit (100 m/s)
    for i in range(len(s) - 1, 0, -1):       # i = last slice, ..., 1
        ...                                  # TODO: three lines, mirroring forward_pass
    return v
""")
code("check_backward(backward_pass, v_cap, kappa, ds, max_brake, grip_share)")
solution("2", """
def backward_pass(v_cap):
    v = np.zeros(len(s))
    v[-1] = min(v_cap[-1], 100.0)
    for i in range(len(s) - 1, 0, -1):
        a = max_brake(v[i]) * grip_share(v[i], kappa[i])
        v_prev = np.sqrt(v[i]**2 + 2 * a * ds)
        v[i - 1] = min(v_prev, v_cap[i - 1])
    return v

check_backward(backward_pass, v_cap, kappa, ds, max_brake, grip_share)
""")

md("""
### Exercise 3: the lap

At every slice the car can go no faster than **either** curve, so the lap is the lower of the two. Then add up the time: each slice takes `ds` ÷ (its average speed).
""")
code("""
def lap_time(v):
    return ...          # TODO 3a: total time (s) for a speed profile v

def solve():
    v_cap = np.array([corner_speed(k) for k in kappa])
    v_fwd = forward_pass(v_cap)
    v_bwd = backward_pass(v_cap)
    v_lap = ...         # TODO 3b: the lower of v_fwd and v_bwd at every slice (one numpy function)
    return v_cap, v_fwd, v_bwd, v_lap
""")
code("check_lap_time(lap_time, ds)")
solution("3", """
def lap_time(v):
    return np.sum(ds / ((v[:-1] + v[1:]) / 2))

def solve():
    v_cap = np.array([corner_speed(k) for k in kappa])
    v_fwd = forward_pass(v_cap)
    v_bwd = backward_pass(v_cap)
    v_lap = np.minimum(v_fwd, v_bwd)
    return v_cap, v_fwd, v_bwd, v_lap

check_lap_time(lap_time, ds)
""")
md("Run your simulation:")
code("""
v_cap, v_fwd, v_bwd, v_lap = solve()
show_lap(s, v_cap, v_fwd, v_bwd, v_lap)
compare(lap_time(v_lap))
""")
md("""
**About 3 s faster than our sim?** Your car is too quick. Where is your orange line above the dashed grey one? Zoom in: `show_lap(s, v_cap, v_fwd, v_bwd, v_lap, zoom=(100, 300))`.
""")

md("""
## 3. Make the model better

### Exercise 4: the friction ellipse

A tyre cannot give full grip sideways **and** full grip forwards at the same time. If a fraction

$$f = \\frac{v^2\\,|\\kappa|}{\\text{max\\_lateral}(v)}$$

of the grip is already used for turning, only $\\sqrt{1 - f^2}$ of it is left for accelerating or braking. Write `grip_share`, then run the simulation again: your forward and backward passes already use it.
""")
code("""
def grip_share(v, kappa):
    return ...          # TODO: the share of grip left for accelerating or braking (never below 0)
""")
code("check_grip_share(grip_share)")
solution("4", """
def grip_share(v, kappa):
    f = v**2 * abs(kappa) / max_lateral(v)
    return np.sqrt(max(0.0, 1 - f**2))

check_grip_share(grip_share)
""")
code("""
v_cap, v_fwd, v_bwd, v_lap = solve()
show_lap(s, v_cap, v_fwd, v_bwd, v_lap)
compare(lap_time(v_lap))
""")
md("""
One line of physics, and your simulation now lands within about half a second of the one the team uses. That is what modelling is: deciding which physics matters.
""")

md("""
### Challenge (if you finish early): weight transfer

When the car accelerates, load moves onto the rear tyres, which are the ones that drive. The extra load on the rear is $m\\,a\\,h / L$ ($h$: height of the centre of gravity, $L$: wheelbase). But how hard you can accelerate depends on the rear grip, and the rear grip depends on $a$:

$$m\\,a = \\mu\\left(\\tfrac{1}{2}(m g + \\text{downforce}) + \\frac{m\\,a\\,h}{L}\\right) - \\text{drag}$$

Solve for $a$. The motor and power limits stay as before; the car still gets the smallest.
""")
code("""
h, L = 0.20, 1.62       # CoG height and wheelbase (m)

def max_accel_with_transfer(v):
    v = max(v, 0.5)
    ...                 # TODO
""")
code("check_max_accel_transfer(max_accel_with_transfer)")
solution("★", """
h, L = 0.20, 1.62

def max_accel_with_transfer(v):
    v = max(v, 0.5)
    a_tyres = (mu * 0.5 * (m * g + downforce(v)) - drag(v)) / (m - mu * m * h / L)
    a_other = (min(T * G * eta / r, P * eta / v) - drag(v)) / m
    return min(a_tyres, a_other)

check_max_accel_transfer(max_accel_with_transfer)
""")
code("""
max_accel = max_accel_with_transfer      # the forward pass now uses the better model
v_cap, v_fwd, v_bwd, v_lap = solve()
show_lap(s, v_cap, v_fwd, v_bwd, v_lap)
compare(lap_time(v_lap))
""")
md("""
Faster again? When the car accelerates, the load moves onto the driven rear tyres, so they grip harder exactly when it helps.
""")

md("""
## What you built

The same algorithm our real simulation uses: corner limits, a forward pass, a backward pass and the lower of the two. Our model goes further: four separate tyres, weight transfer in every direction, the motor's torque curve, where the wings push down, and the battery heating up over a race.

What would **you** improve next? See the ideas at the bottom of the [taster page](https://anjunming1202.github.io/lapsim-taster/), and come and talk to the simulation team.
""")

nb = {"cells": cells, "metadata": {"colab": {"provenance": [], "toc_visible": True}, "kernelspec": {"display_name": "Python 3", "name": "python3"},
      "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 0}
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(nb, fh, ensure_ascii=False, indent=1)
print("wrote", OUT, "with", len(cells), "cells")

# --- test: run every code cell in order, as a student who gets each TODO from the solution
os.chdir(os.path.dirname(os.path.abspath(OUT)))
sys.path.insert(0, os.getcwd())
import matplotlib
matplotlib.use("Agg")
import warnings
warnings.filterwarnings("ignore", message="FigureCanvasAgg is non-interactive")
ns = {}
for i, c in enumerate(cells):
    if c["cell_type"] != "code":
        continue
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(c["source"], f"cell{i}", "exec"), ns)
    text = buf.getvalue().strip()
    if text:
        first = c["source"].splitlines()[0][:60]
        print(f"--- cell {i}: {first}\n{text}")
