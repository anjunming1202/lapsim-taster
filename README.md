# OUR Lap Sim Taster

A hands-on introduction to lap time simulation for the Oxford University Racing freshers taster session. It looks and works like a Colab notebook, but runs entirely in the browser: open it on a phone or laptop and press ▶ on each cell.

**Open it:** https://anjunming1202.github.io/lapsim-taster/ or double-click `index.html`.

## The cells

Each code cell starts with a one-line comment saying what it does.

| Cell | Code | Output | The point |
|---|---|---|---|
| 1 | `load_track` | FSUK 2026 course map | The track is just a line with a curvature at every 10 cm |
| 2 | `load_car` | Parameters next to a top and side view with dimensions | The model is one rigid body on four tyres; these numbers come from the other subteams |
| 3 | `build_ggv`, `forces_at` | 3D GGV and a slice at any speed; drag a point to see the load, force and grip used at each tyre | The GGV is everything the car can do; its edge is where the tyres run out of grip |
| Deep dive (collapsed, under cell 3) | `ggv.add(...)` one law per line | Steps ① to ⑦ carve the GGV one physical law at a time (tyre grip, downforce, weight transfer, driven wheels, motor torque, power limit, drag). Four views: 3D, the g-g slice, accelerate/brake against speed with the tyre, motor and power lines, and cornering against speed. Red is cut away by the law, teal is added. A what-if slider changes that law's number (μ, C_L, CoG height, driven wheels, torque, kW, C_D); *Carve all* plays the steps | Each physical law cuts a specific part of the shape; the top edge is whichever limit is lowest |
| 4 | `corner_limits` … `np.minimum` | One speed chart built up in four steps (① ② ③ ④) | Corners set the speed, accelerating takes distance, braking starts before the corner, the lap is the lower curve |
| 5 | `lap_time`, `replay` | Lap time, then a replay you can move with the progress bar or by clicking or dragging on the track or the speed chart: car on the track, its point on the 3D GGV and on the slice, and a cursor on the speed chart, all in step | The car rides the edge of the GGV almost all lap: it is always at the limit |
| 6 | Colab-style sliders | Same layout as cell 5: race controls and progress bar, then track, 3D GGV and slice, then speed layers and event times. The speed slider compares the two GGVs; playing or dragging the race shows both cars live | Change one number and watch it travel through the simulation |

Then a closing text cell asks *What would you improve?* The examples stay hidden until *Show some examples* is pressed. Each one (fixed aero, a phone-GPS track, simple tyres, no suspension, no heat, a perfect driver, no transients) opens to why it matters and how we could fix it.

Cells depend on each other the way a real notebook does: running cell 4 before cell 3 gives a `NameError`.

## Running the session (5 to 10 minutes)

| Time | Do | Say |
|---|---|---|
| 0–1 min | Cells 1 and 2. | "A lap sim needs two things: a track and a car." |
| 1–3 min | Cell 3: move the speed slider, then *Hard braking* and *Fast corner*. With time to spare (or a curious group), open the deep dive and press *Carve all*. | "This shape is everything the car can do. Its edge is where the tyres run out of grip." |
| 3–5 min | Cell 4: press ① to ④. | "Corner limits, accelerate forwards, brake backwards, take the lower curve." |
| 5–6 min | Cell 5. Point at the dot on the GGV. | "57.45 s. Watch the dot: it stays on the edge of the shape. The car is always at the limit." |
| 6–9 min | Cell 6. Ask the group to guess first, move one slider, then press *Race*. | "Power only changes the straights. Grip changes everything. Mass changes surprisingly little." |
| 9–10 min | *What would you improve?* Let them guess before opening the ideas. | "That is what the simulation team works on." |

Short on time: in cell 3 skip the force presets, and in cell 4 go straight to ④.

## Running a 30-minute session (lab PCs, 5–6 people)

| Time | Do |
|---|---|
| 0–10 min | The page, as in the 10-minute route: cells 1, 3, 4 (press ① to ④) and 5. |
| 10–25 min | Everyone opens **Hands-on notebook** (top right of the page, or the link below) on a lab PC, in pairs, and writes part of the car model and the lap algorithm. |
| 25–30 min | Compare lap times with our sim's 57.45 s, and open *What would you improve?* on the page. |

Notebook: <https://colab.research.google.com/github/anjunming1202/lapsim-taster/blob/main/notebook/lapsim_handson.ipynb> (needs a Google account to run).

Most of the car model is given, one line of physics each, for them to read. They write four pieces:

| Exercise | Writes | Idea | Minutes |
|---|---|---|---|
| 1 | `max_accel(v)` | rear tyres, motor and power each set a limit; the car gets the smallest, minus drag | 3 |
| 2 | `backward_pass` | mirror the given forward pass: brake, working back from the finish | 5 |
| 3 | `lap_time`, `np.minimum` | the lap is the lower curve; time is Σ distance ÷ speed. First result: 54.6 s, 5% fast | 2 |
| 4 | `grip_share` (friction ellipse) | one line of physics: 57.9 s, within 0.5 s of our sim | 3 |
| Challenge | `max_accel_with_transfer` | weight transfer: solve for a when it is on both sides; 56.9 s | for fast pairs |

Every exercise has a check that says what is wrong, and a hidden solution to run when stuck, so nobody gets left behind. Edit the notebook through `notebook/build_notebook.py` (see its docstring).

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
