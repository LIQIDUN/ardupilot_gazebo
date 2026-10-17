# P54 TMECH environment benchmarks

Dedicated branch: `feat/tmech-benchmark-worlds`, based on `eefae265d7f38a2e07be5bba3dbd75c4b4a4e9b2`.
These worlds contain **only static environment collision geometry**: no aircraft, flight-control/ROS plugin,
actuator, downloaded model, or execution interface. Historical worlds and shared models are unchanged.
Loading them is not a flight, a planning experiment, or a full-platform safety demonstration.

## Bundles

- `solar_reference/`: two parallel sloping operation panels, width 2m.
- `shelf_reference/`: the same panels, width 1.2m, with sidewalls and a closed back; front is open.
- Both: slope 20deg, inner normal gap 0.8m, panel length 2.4m, thickness 0.08m, center (3,0,2.2)m.
- Every bundle: `benchmark.world`, `parameters.json`, `obstacles.json`, `targets.json`, `manifest.json`.
- Each obstacle, including the finite ground box, has one real collision and a matching visual box.
  Each bundle defines 27 precontact target poses in JSON, not collision-altering target models in the world.

## Generate and inspect

Run from the Gazebo repository. Choose a **new** output directory: existing bundles are never overwritten.

```bash
python3 tools/tmech_benchmark/generate_world.py --scene solar --width 2.0 --output /tmp/p54_solar_new
python3 tools/tmech_benchmark/generate_world.py --scene shelf --beta-deg 25 --clearance 0.65 --output /tmp/p54_shelf_new
python3 tools/tmech_benchmark/validate_bundle.py /tmp/p54_solar_new
python3 tools/tmech_benchmark/validate_bundle.py /tmp/p54_shelf_new
python3 tools/tmech_benchmark/check_load.py --bundle /tmp/p54_solar_new /tmp/p54_shelf_new --output /tmp/p54_load_new --seconds 40
```

Generator: Python 3.8+ standard library. Validation: NumPy. Load check: installed Gazebo classic `gz`/`gzserver`.
No world/model/plugin compilation is required. The load checker uses an ephemeral localhost master port,
private HOME/log directories, a per-world deadline of at most 60s plus bounded cleanup, paused gzserver,
and queries only. It terminates only its own process group, caps captured server stdout at 512KiB,
and drains/discards excess output without blocking. Internal Gazebo logs are confined to the short-lived
private HOME (their sizes should also be checked in the resulting evidence directory).
It does not run any historical launch script or publish robot commands.

## Geometry/frame contract

- For this project's reader, planner coordinates are `(-y_G, x_G, z_G)`; planner rotation is `Rz(pi/2)*R_G`.
- Scene local u points into the aperture, v is lateral, n is surface-normal. `R_GS=Ry(-beta)`;
  positive beta rises in +u. Clearance is normal distance **between inside faces**, not a z-height difference.
- Obstacle names encode all three box lengths: `obs_box_<lx>_<ly>_<lz>_<role>`.
  Model origins are local bottom-face centers. Collision/visual centers are local `(0,0,lz/2)`;
  link poses and collision orientations are identity. This matches existing `WorldObserver` exactly.
- Ground is a finite 40x40x0.2m collision box, top z=0; candidates must stay within the modeled footprint.
  It is included in `obstacles.json` and the `obs_box_` reader, not silently omitted as a ground plane.
- Positions/lengths: m; angles: rad unless explicitly `*_deg`; quaternions: xyzw.
- The full target tool frame has +x tangent to u, +y=-v, +z towards the lower surface at zero orientation offset.
  Tool offset 0.08m defines a **precontact** pose, not contact/grasp success.
  Its mapping to the planner's 3R scalar orientation and the SDF 5R arm is not verified.
- All solids are static. Friction/contact values are explicit simulator parameters, not calibrated material properties.
  Source OBBs are geometric truth; a center-sampled occupancy grid is not an exact collision model.

See the planning repository `docs/phase1_new/p54_tmech_benchmark/` for source audit, the 18-point geometry
regression, actual WorldObserver/MapManager/SFC-OBB ingestion checks, runtime collision evidence, and the
**unexecuted** A0/A1/A2 pilot plan. No R, manipulability, STRICT-planning, or execution result is claimed here.
