# Entry draft 2: Drive clearances and fit-coupon study

**Status:** review draft from actual AI-assisted computational work, not a completed 7-hour participant session.

**Actual participant time:** __________ (fill only from your own real work log).

**Your contribution / decisions:** __________ (add what you actually reviewed, changed, learned or tested).

## Evidence-based writeup

This review examined the drive interfaces rather than only the overall assembly. The shaft, bushes, rotor, guards, spacer and crank were mapped along the axle. The stack drawing makes gaps visible that still require a real fastener-stack review; the existing assembly is not treated as proof that the retainer hardware is correct.

A fresh 5-degree sweep compared 22 mm, 28 mm and 36 mm crank radii. The 36 mm version interfered with nearby inlet/return geometry. Neither the 22 mm baseline nor the 28 mm candidate showed overlap at the sampled angles. The published machine remains at 22 mm; the larger candidate is not being called approved.

Separate sensitivity calculations examined bore/shaft errors, ball diameter versus pocket diameter, and how rotor thickness consumes the nominal face gaps. Those error values are scenarios, not measurements of a printer. An expanded eight-hole clearance coupon was generated as STEP and STL and checked as a watertight single solid. It has not been printed. The next step is measuring the actual ball and checking the coupon before committing to interface dimensions.

**Assistance:** Ava/Hermes performed the computational analysis, study geometry and evidence-image generation. Do not present this as unaided/manual work.

## Seven evidence images

- `01-axial-stack.png` — Actual stack reveals spacing between crank and retainer still requires hardware review.
- `02-key-cross-section.png` — Source-parameter cross-section; friction and torque capacity not tested.
- `03-bearing-budget.png` — Sensitivity of 8.6mm bore/8mm shaft to opposing dimensional errors.
- `04-crank-sweep.png` — Recreates collision for 36mm and compares 22mm/28mm candidates; current remains 22mm.
- `05-pocket-budget.png` — Computed sensitivity shows why actual ball measurement matters.
- `06-axial-budget.png` — Nominal .4mm per side can be lost to thickness variation; not a printer accuracy claim.
- `07-coupon-study.png` — Drilled-bore coupon generated and mesh-checked for later measured fit tests.
