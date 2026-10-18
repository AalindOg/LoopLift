# Printing — sliced, not physically tested

## What was tested

All 21 part STLs were run through **PrusaSlicer 2.7.2** with a generic FFF profile:

- 256 × 256 mm bed.
- 0.4 mm nozzle, 1.75 mm filament.
- 0.2 mm first and subsequent layers.
- Three perimeters, 20% gyroid infill.
- Buildplate-only supports, 45° threshold.
- 3 mm brim, no skirt.

Each produced nonempty toolpaths without reported warnings. See [checks/slicing-checks.json](checks/slicing-checks.json). Slicing does not test support removal, actual first-layer adhesion, strength, friction or assembled fit.

**Do not print generic test G-code.** None is included. Import the STLs into the actual printer's slicer/profile and inspect every layer, especially the trough bores, bushes, tilted stand tops and thin shaft.

## Orientation

`parts/` files are bed-oriented and translated to Z=0. `assembly-parts/` files retain world assembly coordinates and are for viewing, not direct printing.

- Rotor and guards: flat disc face on bed.
- Tracks: flat sole on bed; catch cups are integrated. Inspect notched transfer lips and supports.
- Baseplate: flat underside on bed. Nut recesses open underneath; inspect bridging and clean the recesses.
- Stand pairs: feet on bed, upright pillars. Support angled mounting faces.
- Shaft: collar on bed; use brim and slow small-perimeter settings.
- Bushes, spacers and knob: bores vertical.
- Funnel/sleeve: axis vertical in local print orientation; support as needed.
- Coupon: flat on bed, before all other parts.

One of each print file is required, except the clearance coupon is only a test piece. The hardware marble is not an STL in the print-parts folder.

## Material and fit

PLA is a reasonable first prototype material; no strength or temperature rating is claimed. Buy/measure a real nominal 8 mm ball rather than relying on a faceted printed marble.

Nominal starting clearances: 9.6 mm rotor pocket diameter, 10 mm channel ID, 8.6 mm bearing bores for the 8 mm shaft, 0.4 mm rotor-face gap, and 3.4 mm M3 clearance holes. Print variation and elephant's foot can change all of these.

The slicing estimates total approximately 263 cm³ across individually sliced pieces, including the generic support/brim choices. At assumed PLA density 1.24 g/cm³ this is about 327 g. Estimated time is roughly 36 h 28 min on that generic profile—not a measured print time or a Bambu-specific prediction.

## First-print checklist

- [ ] Coupon passes with the actual ball/shaft.
- [ ] Rotor holes and guard bores are free of supports and burrs.
- [ ] Empty crank completes a full turn without rubbing.
- [ ] Guard bolts retain the plates without squeezing the rotor.
- [ ] Each cup catches a slow marble and drains into its outgoing trough.
- [ ] Funnel and top outlet transfer work before the whole loop is declared operational.

The known experimental risk is pickup/release and transfer behaviour—not file format. Expect a mechanical revision after testing.
