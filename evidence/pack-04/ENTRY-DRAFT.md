# Entry draft 4: Manufacturing evidence and test-readiness review

**Status:** review draft from actual AI-assisted computational work, not a completed 6-hour participant session.

**Actual participant time:** __________ (fill only from your own real work log).

**Your contribution / decisions:** __________ (add what you actually reviewed, changed, learned or tested).

## Evidence-based writeup

This review audited the published manufacturing outputs and separated what they prove from what remains untested. The 21 print-part mesh records were checked for single-body topology, watertightness and bed placement. The stored generic PrusaSlicer results were then broken down by footprint, height, filament volume and estimated print time. These are existing computational reports being reviewed, not new physical prints.

The baseplate and rotor account for much of the material, while the taller stands need separate attention to adhesion, support removal and stiffness. The fit coupon should be printed before the complete machine. Machine print-time estimates were deliberately kept separate from participant work time.

A verification matrix distinguishes export/geometry checks, the fresh nominal-path audit, the newly found funnel interference, idealised corner screening and missing physical evidence. A prospective seven-stage physical test sequence was prepared, covering measurement, empty rotation, loading, discharge, individual corners, funnel return and repeated full cycles. No stage was marked physically complete. Hardware purchasing and print-ready release remain dependent on those checks.

**Assistance:** Ava/Hermes performed the computational analysis, study geometry and evidence-image generation. Do not present this as unaided/manual work.

## Seven evidence images

- `01-part-inventory.png` — 21 individual published part checks; each expected one solid.
- `02-bed-fit.png` — Computed placement extents; base dominates area while stands dominate height.
- `03-material-breakdown.png` — Per-part slicer filament requirements, not solid-CAD volumes.
- `04-print-time.png` — Existing slicer machine-time estimates explicitly separated from human work.
- `05-orientation-risks.png` — Source dimensions identify tall supports/shaft; angled faces and nut traps still need layer review.
- `06-coverage-matrix.png` — Evidence matrix distinguishes past export validation, fresh audit and remaining physical gates.
- `07-physical-test-plan.png` — Unexecuted acceptance plan is explicitly prospective, not fabricated test evidence.
