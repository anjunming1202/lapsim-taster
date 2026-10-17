# OUR Lap Sim Taster

A hands-on introduction to lap time simulation for the Oxford University Racing freshers taster session. It looks and works like a Colab notebook, but runs entirely in the browser: open it on a phone or laptop and press ▶ on each cell.

**Open it:** https://anjunming1202.github.io/lapsim-taster/ or double-click `index.html`.

## The cells

| Cell | Code | Output | The point |
|---|---|---|---|
| 1 | `load_track` | FSUK 2026 course map | The track is just a line with a curvature at every 10 cm |
| 2 | `load_car` | The car's parameters | These come from the other subteams |
| 3 | `build_ggv` | 3D GGV you can rotate, plus a slice at any speed | Grip is shared between braking, accelerating and turning, and grows with speed |
| 4 | `corner_limits` | Speed limit along the lap | Corners set the speed |
| 5 | `forward_pass` | Flat-out acceleration (green) | Accelerating takes distance |
| 6 | `backward_pass` | Braking, worked backwards (red) | Braking has to start before the corner |
| 7 | `np.minimum` | Lap time, track and speed coloured by accelerating / braking / cornering | That is the whole algorithm |
| 8 | Colab-style form | Your car against the baseline, plus a race | This is what the sim team does every week |

Cells depend on each other the way a real notebook does: running cell 5 before cell 4 gives a `NameError`.

## Running the session (5 to 10 minutes)

| Time | Do | Say |
|---|---|---|
| 0–1 min | Cells 1 and 2. | "A lap sim needs two things: a track and a car." |
| 1–3 min | Cell 3. Drag the speed slider. | "This shape is everything the car can do. Faster means more downforce, so the shape gets bigger." |
| 3–6 min | Cells 4 to 7, one at a time. | "Corner limits, accelerate forwards, brake backwards, take the lower curve. 57.45 s." |
| 6–9 min | Read a "Guess first" question aloud, get guesses, press Try it. | "Other subteams ask us exactly this." |
| 9–10 min | Last text cell. | What the model leaves out, and how to join. |

The bigger-wings question works best: most people expect wings to help everywhere, but the acceleration run gets slower.

**Run all** in the header fills every cell at once, for anyone who arrives late. **Reset** clears the outputs for the next group.

## Where the numbers come from

Every number is pre-computed by the team's lap time simulation, which lives in a private repo. This repo holds only the results (`data/sim.js`): the solver's intermediate stages for the baseline car, its GGV surface, and 225 car setups on a grid of mass × downforce × power limit × tyre grip. The page does no physics itself.

To regenerate after the model changes, run this from the private `lap-sim` repo and commit the new `data/sim.js` here:

```bash
python explore/taster-export/export_taster_data.py --out ../lapsim-taster/data/sim.js
```

Add `--reuse-runs` to recompute only the baseline (about a minute) and keep the 225 grid runs (about 15 minutes).

## Files

```
index.html     the page (no build step, no libraries)
data/sim.js    pre-computed results, loaded with a <script> tag
```
