# OUR Lap Sim Taster

A hands-on introduction to lap time simulation for the Oxford University Racing freshers taster session. It looks and works like a Colab notebook, but runs entirely in the browser: open it on a phone or laptop and press ▶ on each cell.

**Open it:** https://anjunming1202.github.io/lapsim-taster/ or double-click `index.html`.

## The cells

Each code cell starts with a one-line comment saying what it does.

| Cell | Code | Output | The point |
|---|---|---|---|
| 1 | `load_track` | FSUK 2026 course map | The track is just a line with a curvature at every 10 cm |
| 2 | `load_car` | Parameters next to a top and side view with dimensions | The model is one rigid body on four tyres; these numbers come from the other subteams |
| 3 | `build_ggv`, `forces_at` | Steps ① to ⑦ carve the GGV one physical limit at a time (tyre grip, downforce, weight transfer, rear-wheel drive, motor torque, 80 kW limit, drag), shown in 3D and as a slice at any speed; at step ⑦, drag a point to see the forces on each tyre | Each physical limit cuts a specific part of the shape; its edge is where the tyres run out of grip |
| 4 | `corner_limits` … `np.minimum` | One speed chart built up in four steps (① ② ③ ④) | Corners set the speed, accelerating takes distance, braking starts before the corner, the lap is the lower curve |
| 5 | `lap_time`, `replay` | Lap time, then a replay you can move with the progress bar or by clicking or dragging on the track or the speed chart: car on the track, its point on the 3D GGV and on the slice, and a cursor on the speed chart, all in step | The car rides the edge of the GGV almost all lap: it is always at the limit |
| 6 | Colab-style sliders | Same layout as cell 5: race controls and progress bar, then track, 3D GGV and slice, then speed layers and event times. The speed slider compares the two GGVs; playing or dragging the race shows both cars live | Change one number and watch it travel through the simulation |

Then a closing text cell asks *What would you improve?* The examples stay hidden until *Show some examples* is pressed. Each one (fixed aero, a phone-GPS track, simple tyres, no suspension, no heat, a perfect driver, no transients) opens to why it matters and how we could fix it.

Cells depend on each other the way a real notebook does: running cell 4 before cell 3 gives a `NameError`.

## Running the session (5 to 10 minutes)

| Time | Do | Say |
|---|---|---|
| 0–1 min | Cells 1 and 2. | "A lap sim needs two things: a track and a car." |
| 1–3 min | Cell 3. Press ① to ⑦ at 90 km/h, then *Hard braking* and *Fast corner*. | "This shape is everything the car can do. Its edge is where the tyres run out of grip." |
| 3–5 min | Cell 4: press ① to ④. | "Corner limits, accelerate forwards, brake backwards, take the lower curve." |
| 5–6 min | Cell 5. Point at the dot on the GGV. | "57.45 s. Watch the dot: it stays on the edge of the shape. The car is always at the limit." |
| 6–9 min | Cell 6. Ask the group to guess first, move one slider, then press *Race*. | "Power only changes the straights. Grip changes everything. Mass changes surprisingly little." |
| 9–10 min | *What would you improve?* Let them guess before opening the ideas. | "That is what the simulation team works on." |

Short on time: in cell 3 skip the force presets, and in cell 4 go straight to ④.

**Run all** in the header fills every cell at once, for anyone who arrives late. **Reset** clears the outputs for the next group.

## Where the numbers come from

Every number is pre-computed by the team's lap time simulation, which lives in the private `lap-sim` repo. This repo holds only the results (`data/sim.js`): the solver's stages for the baseline car, per-tyre forces on a grid of operating points, and a grid of car setups (mass × downforce × power limit × tyre grip), each with its own GGV and solver stages. The page does no physics itself.

## Updating

| To change | Edit | Then |
|---|---|---|
| The car (mass, CoG, aero, tyres, motor…) | `config/car_default.yaml` in `lap-sim` | Full export |
| The model itself | `lapsim/` in `lap-sim` | Full export |
| The slider values on the page | `GRID` in `lap-sim/explore/taster-export/export_taster_data.py` | Full export |
| Text, layout, colours | `index.html` in this repo | Just commit and push |

The baseline car is always `car_default.yaml` as it stands; its values are added to the slider grid automatically, and drag keeps the yaml's Cd/Cl ratio when downforce changes.

**Full export**, from the `lap-sim` repo root (about 15 minutes on a 32-thread machine):

```bash
.venv\Scripts\activate          # macOS / Linux: source .venv/bin/activate
python explore/taster-export/export_taster_data.py --out ../lapsim-taster/data/sim.js
```

Add `--reuse-runs` to recompute only the baseline car and the force diagrams (about a minute) and keep the existing grid runs. Only use it when the grid would not change.

Then check and publish, from this repo:

```bash
python -m http.server 8000      # open http://localhost:8000 and click Run all
git add data/sim.js index.html
git commit -m "Update taster data"
git push                        # the live page updates about a minute later
```

## Files

```
index.html     the page (no build step, no libraries)
data/sim.js    pre-computed results, loaded with a <script> tag
```
