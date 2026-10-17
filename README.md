# OUR Lap Sim Taster

A hands-on introduction to lap time simulation for the Oxford University Racing freshers taster session. It looks and works like a Colab notebook, but runs entirely in the browser: open it on a phone or laptop and press ▶ on each cell.

**Open it:** https://anjunming1202.github.io/lapsim-taster/ or double-click `index.html`.

## The cells

| Cell | Code | Output | The point |
|---|---|---|---|
| 1 | `load_track` | FSUK 2026 course map | The track is just a line with a curvature at every 10 cm |
| 2 | `load_car` | Parameters, side and top view with dimensions | The model is one rigid body on four tyres; these numbers come from the other subteams |
| 3 | `build_ggv` | 3D GGV you can rotate, plus a slice at any speed | Grip is shared between braking, accelerating and turning, and grows with speed |
| 4 | `ggv.forces_at` | Drag a point inside the GGV; see the load and grip used at each tyre | This is how the GGV is built: its edge is where the tyres reach 100% |
| 5 | `corner_limits` | Speed limit along the lap | Corners set the speed |
| 6 | `forward_pass` | Flat-out acceleration (green) | Accelerating takes distance |
| 7 | `backward_pass` | Braking, worked backwards (red) | Braking has to start before the corner |
| 8 | `np.minimum` | Lap time; track and speed coloured by accelerating / braking / cornering | That is the whole algorithm |
| 9 | Colab-style sliders | Cause chain, results, GGV, speed layers and a race against the baseline | Change one number and watch it travel through the simulation |

Cells depend on each other the way a real notebook does: running cell 6 before cell 5 gives a `NameError`.

## Running the session (5 to 10 minutes)

| Time | Do | Say |
|---|---|---|
| 0–1 min | Cells 1 and 2. | "A lap sim needs two things: a track and a car." |
| 1–3 min | Cell 3, then cell 4: press *Hard braking* and *Fast corner*. | "This shape is everything the car can do. Its edge is where the tyres run out of grip." |
| 3–6 min | Cells 5 to 8, one at a time. | "Corner limits, accelerate forwards, brake backwards, take the lower curve. 57.45 s." |
| 6–9 min | Cell 9. Ask the group to guess first, then move one slider at a time. | "Power only changes the straights. Grip changes everything. Mass changes surprisingly little." |
| 9–10 min | Last text cell. | What the model leaves out, and how to join. |

Short on time: skip cell 4 and the forward/backward cells (6, 7); cell 8 still makes sense on its own.

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
