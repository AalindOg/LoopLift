"""LoopLift return-track profile, ported and substantially modified from
Jan Pieper's openscad/straight-extrude.scad (MIT, copyright 2020 Jan Pieper).
Original notice is preserved in upstream/jhpieper-marble-run/LICENSE.

Changes: symmetric 8 mm ball channel, flat printable sole, no magnet sockets,
optional M3 bolt tabs; analytic CadQuery BREP instead of OpenSCAD extrusion.
Derived geometry is distributed CC BY 4.0; this source is MIT.
"""
import cadquery as cq
BALL_D=8.0
INNER_R=5.0
WALL=2.4
OUTER_R=INNER_R+WALL

def track(length=100.0, tabs=True):
    # Port of source's outer circle minus inner circle and upper-half cut.
    outer=cq.Workplane('YZ').circle(OUTER_R).extrude(length).translate((0,0,OUTER_R))
    # Flat printable sole: original profile also adds a rectangular flat.
    sole=cq.Workplane('XY').box(length,10,2.4,centered=(False,True,False))
    p=outer.union(sole)
    inner=cq.Workplane('YZ').circle(INNER_R).extrude(length+2).translate((-1,0,OUTER_R))
    p=p.cut(inner).cut(cq.Workplane('XY').box(length+2,30,20,centered=(False,True,False)).translate((-1,0,OUTER_R)))
    if tabs:
        for y in [-9.5,9.5]:
            tab=cq.Workplane('XY').box(12,10,3,centered=(True,True,False)).translate((length/2,y,0))
            tab=tab.cut(cq.Workplane('XY').circle(1.7).extrude(3).translate((length/2,y,0)))
            p=p.union(tab)
    return p
