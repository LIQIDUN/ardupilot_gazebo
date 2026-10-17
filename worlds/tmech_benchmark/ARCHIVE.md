# P59 TMECH benchmark archive (2026-10-17)

Dedicated assets only; original Worlds and shared models remain at the parent commit
`eefae265d7f38a2e07be5bba3dbd75c4b4a4e9b2`. Branch: `feat/tmech-benchmark-worlds`.
This archive does not change geometry, generator parameters, physics or historical outputs.

- `solar_reference/`, `shelf_reference/`: P54 reference bundles.
- `p55_pilot/scene_00_solar` through `scene_07_shelf`: eight frozen P55 bundles, reused by P56/P57.
- Every bundle contains `parameters.json`, `benchmark.world`, `obstacles.json`, `targets.json`, `manifest.json`.
- `tools/tmech_benchmark/generate_world.py`: deterministic, no-overwrite generation.
- `validate_bundle.py`: independent XML/collision/visual/OBB/target/hash checks.
- `check_load.py`, `verify_runtime_capture.py`: bounded isolated loading/runtime inspection tools;
  P59 does not launch Gazebo or rerun these runtime experiments.

P54–P57 reports, raw successes/failures, maps, control points and safety audits live in the separate
planning repository `ros_quadtilt/src/aerial_manipulator/docs/phase1_new/`.
Its P59 entry is `docs/RESEARCH_STATUS.md`; parent commit is
`4d826d00cc6458f294564ca1651e2dd32f5ad731`. Keep both archive commits when reproducing.
Bundle manifests describe the geometry-generation stage (`methods_evaluated=[]`), not later planning statistics.

Offline inspection from this repository (does not modify the bundle):

```bash
python3 tools/tmech_benchmark/validate_bundle.py worlds/tmech_benchmark/solar_reference
python3 tools/tmech_benchmark/validate_bundle.py worlds/tmech_benchmark/shelf_reference
```

P59 checks all ten bundles and byte-identical regeneration into temporary new directories;
the machine-readable results are in the planning repository P59 validation folder.
No ARM, flight execution, flight-mode change, shared-model repair or automatic push is part of this archive.
Environment collision consistency is not a full-platform or hardware safety certificate.
