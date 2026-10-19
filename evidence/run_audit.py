#!/usr/bin/env python3
"""Fresh computational audit of existing LoopLift; no claimed human hours.
Writes measured/static and explicitly idealised numerical data for evidence plots.
"""
from pathlib import Path
import sys,json,math,hashlib,time,subprocess
import numpy as np
import cadquery as cq
ROOT=Path(__file__).resolve().parent
PROJECT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT/'cad'))
import build as b
started=time.time()
b.build_lift();b.build_tracks()
by={p['name']:p for p in b.PARTS}
results={'source_commit':subprocess.check_output(['git','-C',str(PROJECT),'rev-parse','HEAD'],text=True).strip(),'build_id':b.SOURCE_HASH,'human_hours':None,'physical_tested':False}

def overlap_ball(point,solids,r=3.98):
 ball=cq.Workplane('XY').sphere(r).translate(tuple(map(float,point))).val()
 return sum(ball.intersect(s.val() if hasattr(s,'val') else s).Volume(1e-7) for s in solids)

def section_segments(shape,y=0):
 # CAD curve intersection gives section edges suitable for a true sectional drawing.
 s=shape.val() if hasattr(shape,'val') else shape
 clip=cq.Workplane('XY').box(1000,.025,1000).translate((0,y,0)).val()
 section=s.intersect(clip)
 verts,faces=section.tessellate(.12)
 return {'vertices':[(v.x,v.y,v.z) for v in verts],'faces':faces}

# Local-coordinate axial passage, centreline only, conservative near-contact radius.
rot=b.rotor();fg=b.guard(True);rg=b.guard();inlet=b.funnel(True);outlet=b.funnel(False)
feed=[]
for z in np.linspace(48,4.2,90):
 feed.append({'z':float(z),'overlap_mm3':overlap_ball((0,-52,z),[rot,fg,inlet])})
discharge=[]
for z in np.linspace(5,-22,70):
 discharge.append({'z':float(z),'overlap_mm3':overlap_ball((0,52,z),[rot,rg,outlet])})
results['feed']={'radius_tested_mm':3.98,'samples':feed,'max_overlap':max(x['overlap_mm3'] for x in feed),'scope':'Fixed indexed pocket, axial centreline only. No rotation during entry.'}
results['discharge']={'samples':discharge,'max_overlap':max(x['overlap_mm3'] for x in discharge),'scope':'Fixed indexed upper pocket, axial centreline only. No dynamics.'}
# Nominal mechanical frame transforms for diagnostics.
results['interfaces']={name:b.world(p) for name,p in {'inlet_mouth':(0,-52,42.4),'inlet_guard':(0,-52,13.4),'bottom_pocket':(0,-52,5),'outlet_end':(0,52,-16.4),'top_pocket':(0,52,5)}.items()}
# Full sphere clearance while indexing at lower port, no adaptive ball centre.
angles=[]
for deg in np.linspace(-4,4,33):
 r=rot.rotate((0,0,0),(0,0,1),float(deg))
 angles.append({'angle':float(deg),'overlap_mm3':overlap_ball((0,-52,8),[r],r=4)})
results['alignment']={'samples':angles,'fixed_ball_diameter_mm':8,'nominal_pocket_diameter_mm':9.6,'pitch_radius_mm':52,'max_centered_angle_deg':math.degrees(2*math.asin(((9.6-8)/2)/(2*52)))}
results['gravity']=[{'tilt_deg':a,'slope_deg':90-a,'axial_g_m_s2':9.81*math.cos(math.radians(a)),'radial_g_m_s2':9.81*math.sin(math.radians(a)),'simple_sliding_mu_limit':math.tan(math.radians(90-a))} for a in range(55,86)]
# Crank comparison: only knobs change orbit radius; arm geometry from original sizing.
static=[p for p in b.PARTS if p['name'] not in ['crank-arm','crank-knob','eight-pocket-rotor','keyed-shaft','shaft-retainer','marble-8mm','clearance-coupon','front-spacer']]
crank=[]
for radius in [22,28,36]:
 for angle in range(0,360,5):
  knob=b.cy(7,22,(radius,0,26.6)).cut(b.cy(1.7,24,(radius,0,25.6)))
  arm=b.cy(10,6,(0,0,20)).union(b.box(radius,12,6,(radius/2,0,23))).union(b.cy(8,6,(radius,0,20)))
  arm=arm.cut(b.key(8,4.2,3.2,19)).cut(b.cy(1.7,8,(radius,0,19)))
  hit=0.;against=[]
  for component in [knob,arm]:
   shape=b.pose(component.rotate((0,0,0),(0,0,1),angle)).val();bb=shape.BoundingBox()
   for p in static:
    pb=p['shape'].BoundingBox()
    if any(min(getattr(bb,k+'max'),getattr(pb,k+'max'))-max(getattr(bb,k+'min'),getattr(pb,k+'min'))<.001 for k in 'xyz'):continue
    v=shape.intersect(p['shape']).Volume(1e-7)
    if v>.05:hit+=v;against.append(p['name'])
  crank.append({'radius_mm':radius,'angle_deg':angle,'overlap_mm3':hit,'against':sorted(set(against))})
results['crank']=crank
# Rigorous dimensions vs sensitivity assumptions (not printer measurements).
results['axial_stack']=[{'name':name,'low':lo,'high':hi} for name,lo,hi in [('rear collar',-12,-9),('rear bush',-9,-4.4),('rear guard',-4.4,-.4),('rotor',0,10),('front guard',10.4,13.4),('front spacer',13.8,20),('crank',20,26),('shaft retainer',33.4,36.4)]]
results['bearing_sensitivity']=[{'diametral_error_mm':float(e),'worst_radial_clearance_mm':(8.6-8-2*e)/2} for e in np.linspace(0,.4,9)]
results['axial_sensitivity']=[{'rotor_growth_mm':float(e),'minimum_face_gap_mm':.4-e/2} for e in np.linspace(0,1,11)]
results['pocket_sensitivity']=[{'pocket_mm':p,'ball_mm':d,'radial_clearance_mm':(p-d)/2} for p in [9.2,9.6,10,10.4] for d in [7.8,8,8.2]]
# Grade and ideal isolated straight-track dynamics, explicitly ignore friction/impact.
g=9810.;trackdata=[]
for name,start,end in b.ROUTES:
 vec=np.array(end)-np.array(start);length=float(np.linalg.norm(vec));drop=float(-vec[2]);unit=vec/length
 # solid sphere rolling from rest: v^2 = 10/7*g*drop
 speed=math.sqrt(10/7*g*drop)
 center_end=np.array(b.point_track((length,0,6.4),start,end))
 center_start=np.array(b.point_track((0,0,6.4),start,end))
 trackdata.append({'name':name,'start':start,'end':end,'center_start':center_start.tolist(),'center_end':center_end.tolist(),'length_mm':length,'drop_mm':drop,'grade_deg':math.degrees(math.asin(drop/length)),'isolated_ideal_speed_mm_s':speed,'unit':unit.tolist()})
results['tracks']=trackdata
transfers=[]
for i in [0,1]:
 incoming=trackdata[i];receiver=trackdata[i+1]
 point=np.array(incoming['center_end']);floor_center=np.array(b.point_track((-1,0,6.4),b.ROUTES[i+1][1],b.ROUTES[i+1][2]))
 fall=float(point[2]-floor_center[2]);speed=incoming['isolated_ideal_speed_mm_s'];v=speed*np.array(incoming['unit']);tau=(v[2]+math.sqrt(v[2]**2+2*g*fall))/g
 landing=point+v*tau+np.array([0,0,-.5*g*tau*tau]);distance=float(np.linalg.norm(landing[:2]-floor_center[:2]))
 samples=[]
 for factor in np.linspace(0,1.3,27):
  vel=v*factor;t=(vel[2]+math.sqrt(vel[2]**2+2*g*fall))/g;land=point+vel*t+np.array([0,0,-.5*g*t*t])
  samples.append({'speed_factor':float(factor),'speed_mm_s':float(speed*factor),'miss_distance_mm':float(np.linalg.norm(land[:2]-floor_center[:2])),'x':float(land[0]),'y':float(land[1])})
 transfers.append({'name':incoming['name']+' to '+receiver['name'],'launch':point.tolist(),'catch_target':floor_center.tolist(),'fall_mm':fall,'nominal_flight_ms':tau*1000,'nominal_landing':landing.tolist(),'center_miss_mm':distance,'nominal_safe_center_radius_mm':8.5-4,'samples':samples,'model':'Ideal no-wall-hit projectile to approximate receiver ball-centre height, from isolated track rolling speed. Rims may intercept the ball; this is a screening bound, not proof of escape.'})
results['transfers']=transfers
# Exact return-to-funnel centreline overlap; detects lip collisions previously excluded.
last=trackdata[-1];samples=[]
length=last['length_mm'];start,end=b.ROUTES[-1][1:]
for f in np.linspace(.8,1.08,36):
 center=b.point_track((length*float(f),0,6.4),start,end)
 samples.append({'fraction':float(f),'center':center,'funnel_overlap_mm3':overlap_ball(center,[by['inlet-funnel']['shape']])})
results['return_funnel']={'samples':samples,'max_overlap':max(s['funnel_overlap_mm3'] for s in samples),'scope':'Straight continuation of final track seated centreline only.'}
# Coupon study: larger set of actual analytic bore cuts, not changed machine.
coupon=b.box(100,45,5,(0,0,2.5))
for x,d in zip([-36,-12,12,36],[8.2,8.4,8.6,8.8]):coupon=coupon.cut(b.cy(d/2,7,(x,-10,-1)))
for x,d in zip([-36,-12,12,36],[9.2,9.6,10,10.4]):coupon=coupon.cut(b.cy(d/2,7,(x,10,-1)))
assert coupon.val().isValid() and len(coupon.val().Solids())==1
(ROOT/'study-parts').mkdir(exist_ok=True)
cq.exporters.export(coupon,str(ROOT/'study-parts/expanded-clearance-coupon.step'))
cq.exporters.export(coupon,str(ROOT/'study-parts/expanded-clearance-coupon.stl'))
results['study_coupon']={'bores_mm':[[8.2,8.4,8.6,8.8],[9.2,9.6,10,10.4]],'valid_solid':True,'volume_mm3':coupon.val().Volume(1e-7),'printed':False}
results['existing_checks']={n:json.loads((PROJECT/'checks'/n).read_text()) for n in ['mesh-checks.json','slicing-checks.json','geometry-checks.json','path-checks.json']}
results['elapsed_compute_seconds']=round(time.time()-started,2)
(ROOT/'audit-results.json').write_text(json.dumps(results,indent=2))
print(json.dumps({'inlet_max_overlap':results['feed']['max_overlap'],'outlet_max_overlap':results['discharge']['max_overlap'],'return_funnel_max_overlap':results['return_funnel']['max_overlap'],'transfer_miss_mm':[t['center_miss_mm'] for t in transfers],'crank_max_overlap_by_radius':{r:max(x['overlap_mm3'] for x in crank if x['radius_mm']==r) for r in [22,28,36]},'seconds':results['elapsed_compute_seconds']},indent=2))
