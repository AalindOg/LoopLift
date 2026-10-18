#!/usr/bin/env python3
"""LoopLift v0.1: inclined pocket elevator + replaceable gravity return.
mm; +Z up. Rotor local XY, tilted 75 deg about X into assembly.
Hand turn slowly, one 8 mm marble. Not physically validated.
"""
from pathlib import Path
import math,json,hashlib,os
import cadquery as cq
from track_profile import track, BALL_D, INNER_R, OUTER_R
ROOT=Path(__file__).resolve().parents[1]
SOURCE_HASH=hashlib.sha256(Path(__file__).read_bytes()+Path(__file__).with_name('track_profile.py').read_bytes()).hexdigest()[:12]
OUT=ROOT/'build'/SOURCE_HASH
PARTS=[];LOCAL={};BASE_HOLES=[]
CRANK_R=22.
TILT=75.;CENTER=(-30,0,105);R=65.;PITCH_R=52.;POCKET_D=9.6
BACK_Z=-4.4; FRONT_Z=10.4;AXLE_R=4.;EAR_X=72.;EAR_Y=32.
COLORS={'frame':(.14,.21,.27),'rotor':(.99,.47,.17),'track':(.20,.69,.69),'guard':(.52,.69,.78),'detail':(.85,.87,.89)}

def wp(s):return s if isinstance(s,cq.Workplane) else cq.Workplane(obj=s)
def box(x,y,z,c):return cq.Workplane('XY').box(x,y,z).translate(c)
def cy(r,h,c=(0,0,0)):return cq.Workplane('XY').circle(r).extrude(h).translate(c)
def pose(s):return wp(s).rotate((0,0,0),(1,0,0),TILT).translate(CENTER)
def world(p):
 x,y,z=p;a=math.radians(TILT)
 return (x+CENTER[0],y*math.cos(a)-z*math.sin(a),CENTER[2]+y*math.sin(a)+z*math.cos(a))
def key(h,r=4,flat=3,z=0):return cy(r,h,(0,0,z)).cut(box(10,20,h+2,(flat+5,0,z+h/2)))
def add(name,local,assembly=None,color='detail',qty=1,printable=True,note=''):
 s=wp(local).val();a=wp(assembly if assembly is not None else local).val()
 for item in [s,a]:
  assert item.isValid() and len(item.Solids())==1 and item.Volume(1e-7)>0,(name,'invalid/empty/disconnected')
 if printable:
  b=s.BoundingBox();s=s.translate((-b.xmin,-b.ymin,-b.zmin))
 PARTS.append(dict(name=name,print_shape=s,shape=a,color=COLORS[color],qty=qty,printable=printable,note=note));LOCAL[name]=wp(local)
 print(name,'ok',flush=True)

def guard(front=False):
 z=FRONT_Z if front else BACK_Z;thick=3 if front else 4
 g=cy(67,thick,(0,0,z))
 for x in [-EAR_X,EAR_X]:
  for y in [-EAR_Y,EAR_Y]:
   g=g.union(box(25,14,thick,(math.copysign(66,x),y,z+thick/2)))
   if not front:g=g.union(cy(4.5,10.8,(x,y,-.4)))
   g=g.cut(cy(1.7,30,(x,y,-12)))
 g=g.cut(cy(4.3,30,(0,0,-12)))
 g=g.cut(cy(5.4 if front else 6,10,(0,-PITCH_R if front else PITCH_R,z-1)))
 # inspection slots inside pocket circle; leave outer retention ring solid
 for sign in [-1,1]:
  slot=box(20,46,thick+2,(sign*21,0,z+thick/2)).edges('|Z').fillet(7)
  g=g.cut(slot)
 return g

def rotor():
 r=cy(R,10)
 for i in range(8):
  angle=-math.pi/2+i*math.pi/4
  r=r.cut(cy(POCKET_D/2,12,(PITCH_R*math.cos(angle),PITCH_R*math.sin(angle),-1)))
 for angle in [0,90,180,270]:
  opening=box(20,12,12,(28,0,5)).edges('|Z').fillet(4).rotate((0,0,0),(0,0,1),angle)
  r=r.cut(opening)
 return r.cut(key(12,4.2,3.2,-1))

def funnel(front=True):
 y=-52 if front else 52
 if front:
  tube=cy(7.8,19,(0,y,13.4)).cut(cy(5.4,22,(0,y,12)))
  cone=cq.Workplane(obj=cq.Solid.makeCone(7.8,14,14,cq.Vector(0,y,28.4)))
  bore=cq.Workplane(obj=cq.Solid.makeCone(5.4,11.6,14.1,cq.Vector(0,y,28.35)))
  tube=tube.union(cone.cut(bore))
 else:
  tube=cy(8,12,(0,y,-16.4)).cut(cy(6,14,(0,y,-17.4)))
 return tube

def build_lift():
 g=guard();f=guard(True);r=rotor()
 add('rear-guard',g,pose(g),'guard',note='Back face on bed; pillars upward. M3 through bolts secure both guards.')
 add('front-guard',f,pose(f),'guard',note='Flat on bed; inlet at lower indexed pocket.')
 add('eight-pocket-rotor',r,pose(r),'rotor',note='Flat on bed. 8 mm ball / 9.6 mm pockets / 0.4 mm axial gaps each side.')
 shaft=key(42,4,3,-9).union(cy(6.5,3,(0,0,-12)))
 shaft=shaft.cut(cy(1.3,14,(0,0,20)))
 add('keyed-shaft',shaft,pose(shaft),'detail',note='Collar on bed; M3 self-tapping retainer pilot. Tall thin print: brim recommended.')
 bush=cy(9,4.6,(0,0,-9)).cut(cy(4.3,5,(0,0,-9.2)))
 add('rear-bush',bush,pose(bush),'detail',note='Separate replaceable printed bearing; 0.3 mm nominal radial clearance.')
 crank=cy(10,6,(0,0,20)).union(box(CRANK_R,12,6,(CRANK_R/2,0,23))).union(cy(8,6,(CRANK_R,0,20)))
 crank=crank.cut(key(8,4.2,3.2,19)).cut(cy(1.7,8,(CRANK_R,0,19)))
 add('crank-arm',crank,pose(crank),'rotor',note='M3 screw + washer at handle; keyed hub. Rotor rotation direction indicated in docs.')
 spacer=cy(6,6.2,(0,0,13.8)).cut(cy(4.3,7,(0,0,13.5)))
 add('front-spacer',spacer,pose(spacer),'detail')
 cap=cy(7,3,(0,0,33.4)).cut(cy(1.7,5,(0,0,32.4)))
 add('shaft-retainer',cap,pose(cap),'rotor',note='M3x12 screw into printed shaft pilot; do not overtighten.')
 knob=cy(7,22,(CRANK_R,0,26.6)).cut(cy(1.7,24,(CRANK_R,0,25.6)))
 add('crank-knob',knob,pose(knob),'detail',note='M3x30 screw, nut and washers; leave free to spin.')
 for front,name in [(True,'inlet-funnel'),(False,'outlet-sleeve')]:
  tube=funnel(front)
  add(name,tube,pose(tube),'track',note='Separate removable chute; attach to guard with a small glue bead after fit test.')
 # Two upright brackets behind lower guard ears, with tilted mating face.
 for sign,side in [(-1,'left'),(1,'right')]:
  cx=sign*EAR_X
  block=box(16,16,6,(cx,-EAR_Y,-8))
  block=block.cut(cy(1.7,10,(cx,-EAR_Y,-13)))
  block=pose(block)
  p=world((cx,-EAR_Y,-8)); px,py,pz=p
  post=box(12,12,pz-6,(px,py,(pz+6)/2))
  foot=box(30,32,5,(px,py,8.5))
  stand=post.union(foot).union(block).cut(pose(g))
  for dy in [-11,11]:
   stand=stand.cut(cy(1.7,8,(px,py+dy,5)));BASE_HOLES.append((px,py+dy))
  add('lift-stand-'+side,stand,None,'frame',note='Upright print; support sloped top block. Bolts align with lower guard ears.')
 # One preview marble; purchase hardware, not a printed sphere.
 ball=cq.Workplane('XY').sphere(4).translate((0,-52,4))
 add('marble-8mm',ball,pose(ball),'detail',printable=False,note='8 mm purchased ball; schematic indexed position, not a dynamic simulation.')

def orient_track(s,start,end):
 dx,dy,dz=[b-a for a,b in zip(start,end)];length=math.sqrt(dx*dx+dy*dy+dz*dz)
 heading=math.degrees(math.atan2(dy,dx));pitch=-math.degrees(math.atan2(dz,math.hypot(dx,dy)))
 return wp(s).rotate((0,0,0),(0,1,0),pitch).rotate((0,0,0),(0,0,1),heading).translate(start)

def point_track(p,start,end):
 dummy=cq.Vertex.makeVertex(*p);return orient_track(dummy,start,end).val().toTuple()

ROUTES=[('upper-return',(-30,31,136),(88,31,121)),
        ('side-return',(88,31,108),(88,-58,96)),
        ('lower-return',(88,-58,83),(-30,-55,70))]

def build_tracks():
 for name,start,end in ROUTES:
  length=math.dist(start,end);p=track(length)
  # widened catch cup at start. Open right side leads into the original-profile trough.
  cup=cy(11,10,(-1,0,0)).cut(cy(8.5,10,(-1,0,2.4)))
  cup=cup.cut(box(24,11,12,(11,0,8.4)))
  p=p.union(cup)
  a=orient_track(p,start,end)
  if name in ['lower-return','upper-return']:
   # Notch transfer lips around the mating sleeve/funnel with a free drop.
   clearance=pose(funnel(name=='lower-return')).val()
   a=a.cut(clearance)
   # Return the notched solid to the part's original print frame.
   dx,dy,dz=[b-a0 for a0,b in zip(start,end)]
   heading=math.degrees(math.atan2(dy,dx));pitch=-math.degrees(math.atan2(dz,math.hypot(dx,dy)))
   p=a.translate(tuple(-x for x in start)).rotate((0,0,0),(0,0,1),-heading).rotate((0,0,0),(0,1,0),-pitch)
  add(name,p,a,'track',note='MIT-derived Jan Pieper profile, 8 mm ball sizing, flat sole, bolted tabs and catch cup.')
  # Support pair with sloped top follows mounting-tab plane exactly.
  points=[point_track((length/2,y,0),start,end) for y in [-9.5,9.5]]
  mx=sum(p[0] for p in points)/2;my=sum(p[1] for p in points)/2
  support=box(26,26,4,(mx,my,8))
  below=orient_track(box(300,300,400,(length/2,0,-200)),start,end)
  for x,y,z in points:
   pillar=cy(4,z+4-6,(x,y,6)).intersect(below)
   pillar=pillar.cut(cy(1.3,14,(x,y,z-12)))
   support=support.union(pillar)
  for dx in [-11,11]:
   support=support.cut(cy(1.7,6,(mx+dx,my,5)));BASE_HOLES.append((mx+dx,my))
  add(name+'-stand',support,None,'frame',note='M3x8 track attachment into printed pilot. 2x M3 base bolts. Post height is fixed to this layout.')
 # small tolerance coupon: shaft holes and pocket gauges only, no detached islands.
 coupon=box(70,24,5,(0,0,2.5))
 for x,d in [(-24,8.2),(-8,8.4),(8,8.6),(24,9.6)]:coupon=coupon.cut(cy(d/2,7,(x,0,-1)))
 add('clearance-coupon',coupon,coupon.translate((0,110,0)),'detail',note='Not installed. Left-to-right holes 8.2 / 8.4 / 8.6 / 9.6 mm; print before mechanism.')
 base=box(220,150,6,(-10,-5,3)).edges('|Z').fillet(8)
 for x,y in BASE_HOLES:
  base=base.cut(cy(1.7,8,(x,y,-1)))
  # underside M3 nut pockets, depth 2.7
  pocket=cq.Workplane('XY').polygon(6,6.6).extrude(2.7).translate((x,y,0))
  base=base.cut(pocket)
 add('baseplate',base,None,'frame',note='Flat bottom. M3 nut traps on underside. Nominal 220x150mm: requires bed margin or a larger bed.')

def export():
 OUT.mkdir(parents=True,exist_ok=True)
 for name in ['parts','assembly-parts']: (OUT/name).mkdir(exist_ok=True)
 assy=cq.Assembly(name='LoopLift');inventory=[]
 for p in PARTS:
  if p['name']=='clearance-coupon':continue
  assy.add(p['shape'],name=p['name'],color=cq.Color(*p['color']))
 for p in PARTS:
  n=p['name'];s=p['shape'];pr=p['print_shape'];b=pr.BoundingBox()
  if p['printable']:cq.exporters.export(pr,str(OUT/'parts'/f'{n}.stl'),tolerance=.06,angularTolerance=.15)
  cq.exporters.export(s,str(OUT/'assembly-parts'/f'{n}.stl'),tolerance=.06,angularTolerance=.15)
  inventory.append({k:v for k,v in p.items() if k not in ['shape','print_shape']}|{'volume_mm3':s.Volume(1e-7),'print_bounds_mm':[b.xlen,b.ylen,b.zlen]})
 assy.export(str(OUT/'LoopLift.step'))
 report={'build_id':SOURCE_HASH,'parts':inventory,'parameters':{'ball_mm':BALL_D,'pocket_mm':POCKET_D,'track_ID_mm':2*INNER_R,'tilt_degrees':TILT,'axial_gap_mm':.4,'rotor_radius_mm':R},'routes':[{'name':n,'start':s,'end':e,'length':math.dist(s,e),'drop':s[2]-e[2]} for n,s,e in ROUTES]}
 (OUT/'inventory.json').write_text(json.dumps(report,indent=2));(ROOT/'build'/'latest.json').write_text(json.dumps({'build_id':SOURCE_HASH}))
 # All installed-part overlaps, except one mathematical marble pose kept separate.
 installed=[p for p in PARTS if p['name'] not in ['clearance-coupon','marble-8mm']]
 clashes=[];errors=[];tested=0
 for i,a in enumerate(installed):
  ba=a['shape'].BoundingBox()
  for b in installed[i+1:]:
   bb=b['shape'].BoundingBox()
   if any(min(getattr(ba,k+'max'),getattr(bb,k+'max'))-max(getattr(ba,k+'min'),getattr(bb,k+'min'))<.001 for k in 'xyz'):continue
   tested+=1
   try:
    v=a['shape'].intersect(b['shape']).Volume(1e-7)
    if v>.5:clashes.append({'a':a['name'],'b':b['name'],'mm3':v})
   except Exception as e:errors.append(str(e))
 # Rotor path envelope, conservative full 65mm disc across all angles.
 sweep=pose(cy(R,10)).val();rotor_clash=[]
 for p in installed:
  if p['name'] in ['eight-pocket-rotor','keyed-shaft']:continue
  v=p['shape'].intersect(sweep).Volume(1e-7)
  if v>.5:rotor_clash.append({'name':p['name'],'mm3':v})
 result={'build_id':SOURCE_HASH,'all_nonempty_valid':True,'installed_instances':len(installed),'collision_threshold_mm3':.5,'tested_pairs':tested,'clashes':clashes,'errors':errors,'rotor_envelope_clashes':rotor_clash,'physical_motion_tested':False}
 (OUT/'geometry-checks.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2),flush=True)
 if clashes or errors or rotor_clash:raise RuntimeError('Geometry checks failed')

if __name__=='__main__':build_lift();build_tracks();export()
