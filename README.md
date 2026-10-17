# OUR Lap Sim Taster

A hands-on introduction to lap time simulation for the Oxford University Racing freshers taster session. It looks and works like a Colab notebook, but runs entirely in the browser: open it on a phone or laptop and press ▶ on each cell.

**Open it:** https://anjunming1202.github.io/lapsim-taster/ or double-click `index.html`.

## The cells

Each code cell starts with a one-line comment saying what it does.

| Cell | Code | Output | The point |
|---|---|---|---|
| 1 | `load_track` | FSUK 2026 course map | The track is just a line with a curvature at every 10 cm |
| 2 | `load_car` | Parameters next to a top and side view with dimensions | The model is one rigid body on four tyres; these numbers come from the other subteams |
| 3 | `build_ggv`, `forces_at` | 3D GGV, a slice at any speed with a draggable point, and the forces on each tyre at that point | The GGV is everything the car can do; its edge is where the tyres reach 100% |
| 4 | `corner_limits` … `np.minimum` | One speed chart built up in four steps (① ② ③ ④) | Corners set the speed, accelerating takes distance, braking starts before the corner, the lap is the lower curve |
| 5 | `lap_time`, `replay` | Lap time, then a replay you can move with the progress bar or by clicking or dragging on the track or the speed chart: car on the track, its point on the 3D GGV and on the slice, and a cursor on the speed chart, all in step | The car rides the edge of the GGV almost all lap: it is always at the limit |
| 6 | Colab-style sliders | Same layout as cell 5: race controls and progress bar, then track, 3D GGV and slice, then speed layers and event times. The speed slider compares the two GGVs; playing or dragging the race shows both cars live | Change one number and watch it travel through the simulation |

Then a closing text cell asks *What would you improve?* The examples stay hidden until *Show some examples* is pressed. Each one (fixed aero, a phone-GPS track, simple tyres, no suspension, no heat, a perfect driver, no transients) opens to why it matters and how we could fix it.

Cells depend on each other the way a real notebook does: running cell 4 before cell 3 gives a `NameError`.

## Running the session (5 to 10 minutes)

| Time | Do | Say |
|---|---|---|
| 0–1 min | Cells 1 and 2. | "A lap sim needs two things: a track and a car." |
| 1–3 min | Cell 3. Move the speed slider, then press *Hard braking* and *Fast corner*. | "This shape is everything the car can do. Its edge is where the tyres run out of grip." |
| 3–5 min | Cell 4: press ① to ④. | "Corner limits, accelerate forwards, brake backwards, take the lower curve." |
| 5–6 min | Cell 5. Point at the dot on the GGV. | "57.45 s. Watch the dot: it stays on the edge of the shape. The car is always at the limit." |
| 6–9 min | Cell 6. Ask the group to guess first, move one slider, then press *Race*. | "Power only changes the straights. Grip changes everything. Mass changes surprisingly little." |
| 9–10 min | *What would you improve?* Let them guess before opening the ideas. | "That is what the simulation team works on." |

Short on time: in cell 3 skip the force presets, and in cell 4 go straight to ④.

**Run all** in the header fills every cell at once, for anyone who arrives late. **Reset** clears the outputs for the next group.

## Where the numbers come from

Every number is pre-computed by the team's lap time simulation, which lives in a private repo. This repo holds only the results (`data/sim.js`): the solver's stages for the baseline car, per-tyre forces on a grid of operating points, and 225 car setups on a grid of mass × downforce × power limit × tyre grip, each with its own GGV and solver stages. The page does no physics itself.

To regenerate after the model changes, run this from the private `lap-sim` repo and commit the new `data/sim.js` here:

```bash
python explore/taster-export/export_taster_data.py --out ../lapsim-taster/data/sim.js
```

Add `--reuse-runs` to recompute only the baseline (about a minute) and keep the 225 grid runs (30 to 40 minutes).

## Files

```
index.html     the page (no build step, no libraries)
data/sim.js    pre-computed results, loaded with a <script> tag
```
