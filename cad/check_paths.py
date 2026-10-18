#!/usr/bin/env python3
"""Nominal path checks; friction, restitution and dynamic capture NOT simulated."""
import importlib.util,json,math,hashlib
from pathlib import Path
import cadquery as cq
import build as b
ROOT=Path(__file__).resolve().parents[1];out=b.OUT
# Build through the same frozen module source; no second source of geometry.
b.build_lift();b.build_tracks()
by={p['name']:p['shape'] for p in b.PARTS}
records=[];fail=[]
# A seated 8mm sphere is moved through 24 indexed rotor angles, in its own pocket.
for angle in range(0,360,15):
 local_ball=cq.Workplane('XY').sphere(4).translate((0,-52,5)).rotate((0,0,0),(0,0,1),angle)
 ball=b.pose(local_ball).val()
 rotor=b.pose(b.rotor().rotate((0,0,0),(0,0,1),angle)).val()
 v=ball.intersect(rotor).Volume(1e-7)
 vg=sum(ball.intersect(by[n]).Volume(1e-7) for n in ['rear-guard','front-guard'])
 records.append({'angle_degrees':angle,'ball_rotor_overlap_mm3':v,'ball_guard_overlap_mm3':vg})
 if v>.05 or vg>.05:fail.append(records[-1])
# Sampling central straight channel; joint cups checked separately and physically pending.
tracks=[]
for name,start,end in b.ROUTES:
 length=math.dist(start,end);samples=[]
 for f in [.15,.3,.5,.7,.85]:
  # Half-round trough inner center is 7.4, radius 5: seated r4 center at6.4.
  center=b.point_track((length*f,0,6.4),start,end)
  ball=cq.Workplane('XY').sphere(3.98).translate(center).val()
  overlap=ball.intersect(by[name]).Volume(1e-7)
  samples.append({'fraction':f,'center':center,'overlap_mm3':overlap})
  if overlap>.1:fail.append({'track':name,'fraction':f,'overlap':overlap})
 tracks.append({'name':name,'drop_mm':start[2]-end[2],'samples':samples})
# Sample crank sweep against all stationary bodies. Fasteners/fingers are not modeled.
crank_hits=[]
static=[p for p in b.PARTS if p['name'] not in ['crank-arm','crank-knob','eight-pocket-rotor','keyed-shaft','shaft-retainer','marble-8mm','clearance-coupon','front-spacer']]
for angle in range(0,360,15):
 for name in ['crank-arm','crank-knob']:
  shape=b.pose(b.LOCAL[name].rotate((0,0,0),(0,0,1),angle)).val();bb=shape.BoundingBox()
  for p in static:
   pb=p['shape'].BoundingBox()
   if any(min(getattr(bb,k+'max'),getattr(pb,k+'max'))-max(getattr(bb,k+'min'),getattr(pb,k+'min'))<.001 for k in 'xyz'):continue
   v=shape.intersect(p['shape']).Volume(1e-7)
   if v>.5:crank_hits.append({'angle':angle,'part':name,'against':p['name'],'mm3':v})
fail.extend(crank_hits)
report={'build_id':b.SOURCE_HASH,'crank_sampled_angles':24,'crank_clashes':crank_hits,'rotor_seated_ball_samples':records,'track_samples':tracks,'failures':fail,
 'passed_nominal_samples':not fail,'scope':'Geometric seated-ball clearance in pocket and straight trough segments ONLY.',
 'not_verified':['inlet capture while rotor moves','outlet release timing','ballistic cup catches','funnel capture','friction/rolling','wear','real printed tolerances']}
(out/'path-checks.json').write_text(json.dumps(report,indent=2));print(json.dumps({'passed':not fail,'rotor_angles':len(records),'track_samples':sum(len(t['samples']) for t in tracks),'failures':fail},indent=2));assert not fail
