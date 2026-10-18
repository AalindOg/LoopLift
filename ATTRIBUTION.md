# Attribution and existing designs

## Yes, similar machines already exist

This is an educational mechanical remix, **not a claim to have invented marble lifts or modular marble runs**.

| Project | What was checked | Reuse decision |
| --- | --- | --- |
| [Jan Pieper — marble-run](https://github.com/jhpieper/marble-run) | Editable OpenSCAD tracks, wheels, switchers and magnetic mounts; MIT code and a separate CC BY 4.0 STL note | Downloaded pinned source. Adapted the straight-track profile into CadQuery; removed magnetic mounting and redesigned its scale, sole, mount tabs and catches. |
| [Out Of Marbles — hand-cranked bucket lift](https://www.printables.com/model/326261-bucket-lift-modular-marble-machine-handcranked) | Prior art for a hand-cranked modular marble machine; public description allows modified uploads under its license and forbids resale of its digital/printed versions | Research reference only. No files copied into LoopLift. |
| [koen-lee — marble run drive](https://github.com/koen-lee/OpenSCAD-designs/blob/master/marble%20run%20drive.scad) | MIT repository; belt/pulley shapes | Inspected, not used. A pulley does not solve pickup/release. |
| [karnxx — merbl](https://github.com/karnxx/merbl) | Half Life learning guide and STEP file; no license file detected during review | Inspiration/learning reference only. No source or STEP copied. |

## Pinned upstream snapshot

Repository: `jhpieper/marble-run`

Commit: `64b8f62091775c56ffcdbe276b6a8cbad95581f7`

The original `LICENSE`, `README.md`, `openscad/straight-extrude.scad` and `openscad/wheel.scad` are preserved under `upstream/jhpieper-marble-run/`. Their hashes are recorded in [upstream/source.json](upstream/source.json).

The original straight track was rendered with OpenSCAD 2021.01 as an actual source check. `wheel.scad` was inspected for comparison, **not used to claim the elevator rotor as a derivative of that file**. The new elevator uses through-pockets and tilted guards, not the upstream paddle wheel.

## Exact derivative boundary

[`cad/track_profile.py`](cad/track_profile.py) ports the upstream straight track's subtractive circular channel/flat-section construction. It is not an STL rename:

- Smaller symmetric channel for nominal 8 mm marbles.
- Flat print sole and 2.4 mm nominal wall.
- No magnet sockets.
- Two drilled bolt tabs.
- Per-layout lengths, descending installation transforms and integrated catch cups.

[`cad/build.py`](cad/build.py) adds the new tilted lift, eight-pocket rotor, guards, keyed shaft, crank, inlet/outlet, freestanding mounts, return layout and clearance coupon. These additions were AI-assisted procedural CAD, not manually modeled hours claimed by the project owner.

## Half Life submission honesty

The challenge requires meaningful personal design changes. Licensing permits reuse but does not guarantee programme eligibility. This repo documents the real changes and AI assistance; it does not invent time logs, unaided authorship, fabricated parts or a successful marble cycle. The participant must review, understand, test and accurately journal their own work. No platform submission has been made by publishing this repo.
