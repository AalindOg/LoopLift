# Entry draft 1: Feed and discharge audit

**Status:** review draft from actual AI-assisted computational work, not a completed 7-hour participant session.

**Actual participant time:** __________ (fill only from your own real work log).

**Your contribution / decisions:** __________ (add what you actually reviewed, changed, learned or tested).

## Evidence-based writeup

This review focused on whether an 8 mm marble has an unobstructed path into and out of the existing LoopLift rotor. The source geometry was inspected in section, and fresh sphere–solid intersections were run along the lower inlet and upper outlet with the rotor held at the correct index. The 90 inlet positions and 70 outlet positions reported no overlap for a 3.98 mm-radius test sphere.

That result is narrower than saying the lift works. A separate alignment sweep showed how quickly the pocket begins to interfere when the rotor moves away from the loading position. The nominal centred angular clearance is about ±0.88 degrees. The gravity study also shows that a steep rotor gives a comparatively small gravity component along the axle. Loading while turning, friction and release timing still need testing.

The concrete output is a set of true CAD sections, two clearance plots, an alignment plot and a tilt study. No physical marble cycle was tested, and no machine geometry was changed in this pack. The next work is to review the loading window and test the inlet with one ball before adding more.

**Assistance:** Ava/Hermes performed the computational analysis, study geometry and evidence-image generation. Do not present this as unaided/manual work.

## Seven evidence images

- `01-interface-map.png` — Source-derived inlet, seated-pocket and outlet world positions.
- `02-inlet-section.png` — True CAD section and tested near-contact sphere positions.
- `03-inlet-clearance.png` — 90 executed Boolean checks along the aligned lower centreline.
- `04-outlet-section.png` — Actual upper outlet section with sampled sphere positions.
- `05-outlet-clearance.png` — 70 exact sphere/rotor/guard/sleeve checks.
- `06-alignment-window.png` — Executed indexed entry-angle overlap sweep and geometric angular-clearance limit.
- `07-tilt-gravity.png` — Computed decomposition highlights weak axial gravity at steep tilt.
