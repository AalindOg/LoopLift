# LoopLift evidence packs — review before journaling

There are four thematic packs with seven individual PNGs each, plus an entry draft. This is **28 technical evidence images**, not a record of 27 hours already worked.

The proposed human work budget is 7 + 7 + 7 + 6 = 27 hours. That is a plan only. The computation and image generation were performed by Ava/Hermes; only the participant’s actual review, design, testing and documentation time should be logged according to programme rules. Do not backdate these packs or post the plan as completed sessions.

## Open each evidence gallery

- [Pack 1: feed and discharge](pack-01/README.md) · [entry draft](pack-01/ENTRY-DRAFT.md)
- [Pack 2: drive and tolerances](pack-02/README.md) · [entry draft](pack-02/ENTRY-DRAFT.md)
- [Pack 3: return path](pack-03/README.md) · [entry draft](pack-03/ENTRY-DRAFT.md)
- [Pack 4: print preparation](pack-04/README.md) · [entry draft](pack-04/ENTRY-DRAFT.md)
- [Progress reels](../media/README.md) · [Priced shopping list](../shopping/README.md)

## What is inside
- `pack-01/`: feed/discharge sections, exact static-path checks and alignment/tilt analysis.
- `pack-02/`: drive stack, dimensional sensitivities, crank comparison and expanded coupon study.
- `pack-03/`: track/transfer screening, actual funnel interference and two separate relief studies.
- `pack-04/`: baseline mesh/slicer evidence review and prospective physical acceptance plan.
- `study-parts/`: new coupon and funnel-relief study STEP/STL files. They are **not** merged into the published machine, nor print-proven.
- `audit-results.json`, `relief-results.json`, `relief-v1-results.json`: raw calculation/check results.
- Python scripts: reproduce the analyses and images from the pinned local LoopLift source.
- `WORK-PLAN.md`: prospective work blocks, not earned hours.
- `review/`: small contact sheets for navigation; not extra evidence subjects.

## Critical finding
The prior build’s static assembly and interior straight-track checks did not establish working return transfers. A new sphere-centreline check detects funnel-lip interference. A separate relief candidate clears the sampled path but is not yet qualified for retention, strength or dynamics. Corner trajectories are idealised screening calculations—not physical simulation or observed failures.

Nothing was uploaded to Half Life, and no time entries were created. The published GitHub model was not silently replaced by a study candidate.

## Reproduce the analysis

From the repository root, using a Python environment with the root requirements and `matplotlib`:

```sh
python -m pip install -r evidence/requirements.txt
python evidence/run_audit.py
python evidence/study_relief.py
python evidence/make_images.py
```

These commands regenerate their local reports, candidate exports and images. The first relief failure is retained as `relief-v1-results.json`; `study_relief.py` regenerates the extended candidate. Baseline CAD source and assembly exports remain separate and unchanged.
