# OUR Lap Sim Taster

A hands-on introduction to lap time simulation for the Oxford University Racing freshers taster session. It looks and works like a Colab notebook, but runs entirely in the browser: open it on a phone or laptop and press ▶ on each cell.

**Open it:** https://anjunming1202.github.io/lapsim-taster/ or double-click `index.html`.

## The cells

| Cell | Code | Output | The point |
|---|---|---|---|
| 1 | `load_track` | FSUK 2026 course map | The track is just a line with a curvature at every 10 cm |
| 2 | `load_car` | Parameters next to a top and side view with dimensions | The model is one rigid body on four tyres; these numbers come from the other subteams |
| 3 | `build_ggv`, `forces_at` | 3D GGV, a slice at any speed with a draggable point, and the forces on each tyre at that point | The GGV is everything the car can do; its edge is where the tyres reach 100% |
| 4 | `corner_limits`, `forward_pass`, `backward_pass` | One speed chart built up in three steps (① ② ③) | Corners set the speed, accelerating takes distance, braking starts before the corner |
| 5 | `np.minimum` | Lap time; track and speed coloured by accelerating / braking / cornering | That is the whole algorithm |
| 6 | Colab-style sliders | Cause chain, speed layers, GGV against the baseline, track, event times, race | Change one number and watch it travel through the simulation |

Cells depend on each other the way a real notebook does: running cell 4 before cell 3 gives a `NameError`.

## Running the session (5 to 10 minutes)

| Time | Do | Say |
|---|---|---|
| 0–1 min | Cells 1 and 2. | "A lap sim needs two things: a track and a car." |
| 1–3 min | Cell 3. Move the speed slider, then press *Hard braking* and *Fast corner*. | "This shape is everything the car can do. Its edge is where the tyres run out of grip." |
| 3–5 min | Cell 4: press ①, ②, ③. Then cell 5. | "Corner limits, accelerate forwards, brake backwards, take the lower curve. 57.45 s." |
| 5–9 min | Cell 6. Ask the group to guess first, then move one slider at a time. | "Power only changes the straights. Grip changes everything. Mass changes surprisingly little." |
| 9–10 min | Last text cell. | What the model leaves out, and how to join. |

Short on time: in cell 3 skip the force presets, and in cell 4 go straight to ③.

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
