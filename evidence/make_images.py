#!/usr/bin/env python3
"""28 evidence images from actual audit data, with explicit scope limitations."""
from pathlib import Path
import json,math,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Rectangle,Polygon
from matplotlib.collections import PolyCollection
from PIL import Image,ImageOps,ImageDraw,ImageFont
import cadquery as cq
ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'audit-results.json').read_text());R=json.loads((ROOT/'relief-results.json').read_text());R1=json.loads((ROOT/'relief-v1-results.json').read_text())
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'cad'));import build as b
COL=['#ff9447','#26a7ac','#7598b0','#6c75c6'];BG='#f6f8fb';INK='#173344';MUTED='#526876'
plt.rcParams.update({'figure.facecolor':BG,'axes.facecolor':'white','axes.edgecolor':'#bdcbd5','axes.labelcolor':INK,'text.color':INK,'xtick.color':MUTED,'ytick.color':MUTED,'font.size':12,'axes.titleweight':'bold','axes.titlesize':15,'grid.alpha':.2,'font.family':'DejaVu Sans'})
manifest=[]

def fig(title,sub='',cols=1):
 f,axes=plt.subplots(1,cols,figsize=(14,9),dpi=125,squeeze=False)
 f.suptitle(title,x=.07,ha='left',fontsize=22,fontweight='bold',y=.965)
 f.text(.07,.915,sub,fontsize=12,color=MUTED)
 f.subplots_adjust(left=.09,right=.96,bottom=.16,top=.86,wspace=.3)
 f.text(.07,.055,'LoopLift / AI-assisted engineering review / source '+D['source_commit'][:7],fontsize=10,color=MUTED)
 f.text(.07,.03,'Computational evidence, not a record of human hours or physical testing.',fontsize=10,color=MUTED)
 return f,axes[0] if cols>1 else axes[0,0]

def save(f,group,num,name,description):
 folder=ROOT/f'pack-{group:02d}';folder.mkdir(exist_ok=True)
 path=folder/f'{num:02d}-{name}.png';f.savefig(path);plt.close(f)
 manifest.append({'pack':group,'image':str(path.relative_to(ROOT)),'evidence':description})

def sec(ax,shape,color):
 s=shape.val() if isinstance(shape,cq.Workplane) else shape
 slab=b.box(.05,180,180,(0,0,0)).val();s=s.intersect(slab)
 verts,faces=s.tessellate(.08)
 pts=np.array([(v.z,v.y) for v in verts]);polys=[pts[list(face)] for face in faces]
 ax.add_collection(PolyCollection(polys,facecolors=color,edgecolors='none'))

def bars(ax,names,values,xlabel,color=COL[0]):
 ax.figure.subplots_adjust(left=.27)
 y=np.arange(len(names));ax.barh(y,values,color=color);ax.set_yticks(y,names);ax.invert_yaxis();ax.set_xlabel(xlabel);ax.grid(axis='x')
 for i,v in enumerate(values):ax.text(v+max(values)*.012,i,f'{v:.1f}',va='center',fontsize=10)
 ax.set_xlim(0,max(values)*1.18)

# 1. Feed/discharge evidence
f,ax=fig('01 / Feed and discharge interface map','Actual assembly-coordinate points from the source transforms.')
for name,p in D['interfaces'].items():
 ax.scatter(p[1],p[2],s=100);ax.annotate(name.replace('_',' '),(p[1],p[2]),xytext=(8,7),textcoords='offset points',fontsize=10)
for names in [('inlet_mouth','inlet_guard','bottom_pocket'),('top_pocket','outlet_end')]:
 coords=[D['interfaces'][n] for n in names];ax.plot([p[1] for p in coords],[p[2] for p in coords],lw=3)
ax.set(xlabel='World Y (mm)',ylabel='World Z (mm)');ax.grid();save(f,1,1,'interface-map','Source-derived inlet, seated-pocket and outlet world positions.')
f,ax=fig('02 / Lower loading path: section through CAD','Thin solid section at local X = 0; an indexed, stationary pocket.')
for s,c in [(b.guard(),COL[2]),(b.guard(True),COL[2]),(b.rotor(),COL[0]),(b.funnel(True),COL[1])]:sec(ax,s,c)
for z in [5,19,35,47]:ax.add_patch(Circle((z,-52),3.98,fill=False,edgecolor=INK,lw=1.5))
ax.set(xlim=(-12,53),ylim=(-68,-33),xlabel='Local axial Z (mm)',ylabel='Local radial Y (mm)');ax.set_aspect('equal');ax.grid();save(f,1,2,'inlet-section','True CAD section and tested near-contact sphere positions.')
f,ax=fig('03 / Inlet centreline clearance','Exact sphere–solid intersections; sphere radius 3.98 mm, rotor fixed in alignment.')
a=D['feed']['samples'];ax.plot([x['z'] for x in a],[x['overlap_mm3'] for x in a],lw=3,color=COL[1]);ax.set(xlabel='Sphere centre, local axial Z (mm)',ylabel='Intersection volume (mm³)',ylim=(-.1,1));ax.grid();ax.text(.05,.75,f"{len(a)} samples / max overlap {D['feed']['max_overlap']:.3f} mm³\nPasses this static path—not self-feeding while turning.",transform=ax.transAxes,fontsize=16);save(f,1,3,'inlet-clearance','90 executed Boolean checks along the aligned lower centreline.')
f,ax=fig('04 / Upper release path: section through CAD','The sleeve exits behind the rear guard. Solid section at local X = 0.')
for s,c in [(b.guard(),COL[2]),(b.guard(True),COL[2]),(b.rotor(),COL[0]),(b.funnel(False),COL[1])]:sec(ax,s,c)
for z in [5,-7,-19]:ax.add_patch(Circle((z,52),3.98,fill=False,edgecolor=INK,lw=1.5))
ax.set(xlim=(-28,19),ylim=(35,68),xlabel='Local axial Z (mm)',ylabel='Local radial Y (mm)');ax.set_aspect('equal');ax.grid();save(f,1,4,'outlet-section','Actual upper outlet section with sampled sphere positions.')
f,ax=fig('05 / Outlet centreline clearance','Stationary upper pocket only: retention and release timing are separate questions.')
a=D['discharge']['samples'];ax.plot([x['z'] for x in a],[x['overlap_mm3'] for x in a],color=COL[1],lw=3);ax.set(xlabel='Sphere centre, local axial Z (mm)',ylabel='Intersection volume (mm³)',ylim=(-.1,1));ax.grid();ax.text(.05,.75,f"{len(a)} samples / max overlap {D['discharge']['max_overlap']:.3f} mm³\nNo static centreline obstruction found.",transform=ax.transAxes,fontsize=16);save(f,1,5,'outlet-clearance','70 exact sphere/rotor/guard/sleeve checks.')
f,ax=fig('06 / Loading alignment is a narrow window','8 mm sphere at local Z = 8 mm; rotate the pocket, hold the sphere fixed.')
a=D['alignment']['samples'];ax.plot([x['angle'] for x in a],[x['overlap_mm3'] for x in a],color=COL[0],lw=3);v=D['alignment']['max_centered_angle_deg'];ax.axvspan(-v,v,color=COL[1],alpha=.2,label=f'Nominal centred clearance ±{v:.2f}°');ax.legend();ax.set(xlabel='Rotor offset (degrees)',ylabel='Ball–rotor overlap (mm³)');ax.grid();save(f,1,6,'alignment-window','Executed indexed entry-angle overlap sweep and geometric angular-clearance limit.')
f,ax=fig('07 / Tilt trade-off: gravity along the bore','Analytical gravity decomposition—not measured friction or a motion simulation.')
a=D['gravity'];ax.plot([x['tilt_deg'] for x in a],[x['axial_g_m_s2'] for x in a],lw=3,label='Gravity along axle');ax.plot([x['tilt_deg'] for x in a],[x['radial_g_m_s2'] for x in a],lw=3,label='Gravity in rotor plane');ax.axvline(75,color=INK,ls='--',label='Current 75° tilt');ax.set(xlabel='Rotor-plane angle from horizontal (degrees)',ylabel='Acceleration component (m/s²)');ax.grid();ax.legend();save(f,1,7,'tilt-gravity','Computed decomposition highlights weak axial gravity at steep tilt.')
# 2. drive
f,ax=fig('01 / Axial stack audit','Source extents on the local axle. Empty spaces are real nominal gaps, not fitted hardware.')
stack=D['axial_stack'];
for i,s in enumerate(stack):ax.barh(i,s['high']-s['low'],left=s['low'],color=COL[i%4]);ax.text(s['high']+.4,i,f"{s['low']:g} … {s['high']:g}",va='center',fontsize=10)
ax.set_yticks(range(len(stack)),[s['name'] for s in stack]);ax.invert_yaxis();ax.set(xlabel='Local axial Z (mm)',xlim=(-15,46));ax.grid(axis='x');save(f,2,1,'axial-stack','Actual stack reveals spacing between crank and retainer still requires hardware review.')
f,ax=fig('02 / D-key interface','Analytic nominal cross-sections: shaft radius 4 / bore radius 4.2 mm; flats 3 / 3.2 mm.')
th=np.linspace(0,2*np.pi,600)
for r,flat,c,label in [(4.2,3.2,COL[2],'bore'),(4,3,COL[0],'shaft')]:
 x=r*np.cos(th);y=r*np.sin(th);mask=x<=flat;x=x[mask];y=y[mask];ax.fill(np.r_[x,x[0]],np.r_[y,y[0]],color=c,alpha=.6,label=label)
ax.set_aspect('equal');ax.set(xlabel='Local X (mm)',ylabel='Local Y (mm)');ax.grid();ax.legend();save(f,2,2,'key-cross-section','Source-parameter cross-section; friction and torque capacity not tested.')
f,ax=fig('03 / Bearing fit tolerance budget','Scenario: bore shrinks by e and shaft grows by e, both diametrally. These are assumed errors.')
a=D['bearing_sensitivity'];ax.plot([x['diametral_error_mm'] for x in a],[x['worst_radial_clearance_mm'] for x in a],marker='o',lw=3);ax.axhline(0,color='#d24d4d',ls='--');ax.set(xlabel='Assumed error per diameter e (mm)',ylabel='Remaining radial clearance (mm)');ax.grid();save(f,2,3,'bearing-budget','Sensitivity of 8.6mm bore/8mm shaft to opposing dimensional errors.')
f,ax=fig('04 / Crank-radius collision comparison','Fresh exact arm + knob sweep, 5° samples against stationary solids.')
for r in [22,28,36]:
 a=[x for x in D['crank'] if x['radius_mm']==r];ax.plot([x['angle_deg'] for x in a],[x['overlap_mm3'] for x in a],lw=2,label=f'{r} mm crank radius')
ax.set(xlabel='Crank angle (degrees)',ylabel='Total detected overlap (mm³)');ax.grid();ax.legend();save(f,2,4,'crank-sweep','Recreates collision for 36mm and compares 22mm/28mm candidates; current remains 22mm.')
f,ax=fig('05 / Ball-to-pocket clearance sensitivity','Nominal dimension sweep—not measured marble variation.')
for p in [9.2,9.6,10,10.4]:
 a=[x for x in D['pocket_sensitivity'] if x['pocket_mm']==p];ax.plot([x['ball_mm'] for x in a],[x['radial_clearance_mm'] for x in a],marker='o',label=f'{p:g} mm pocket')
ax.set(xlabel='Assumed actual ball diameter (mm)',ylabel='Radial clearance (mm)');ax.legend();ax.grid();save(f,2,5,'pocket-budget','Computed sensitivity shows why actual ball measurement matters.')
f,ax=fig('06 / Rotor thickness consumes the face gaps','Fixed guard spacing; rotor centred. Actual plate warp / off-centre assembly can be worse.')
a=D['axial_sensitivity'];ax.plot([x['rotor_growth_mm'] for x in a],[x['minimum_face_gap_mm'] for x in a],marker='o',color=COL[0],lw=3);ax.axhline(0,color='#d24d4d',ls='--');ax.set(xlabel='Assumed rotor thickness increase (mm)',ylabel='Face clearance on each side (mm)');ax.grid();save(f,2,6,'axial-budget','Nominal .4mm per side can be lost to thickness variation; not a printer accuracy claim.')
f,ax=fig('07 / Expanded clearance-coupon study','New separate STEP/STL: 100 × 45 × 5 mm. Watertight single solid; not printed.')
ax.add_patch(Rectangle((-50,-22.5),100,45,facecolor=COL[2],alpha=.65))
for y,ds in [(-10,[8.2,8.4,8.6,8.8]),(10,[9.2,9.6,10,10.4])]:
 for x,d in zip([-36,-12,12,36],ds):ax.add_patch(Circle((x,y),d/2,facecolor='white',edgecolor=INK));ax.text(x,y+7,str(d),ha='center',fontsize=11)
ax.set(xlim=(-55,55),ylim=(-27,30),xlabel='X (mm)',ylabel='Y (mm)');ax.set_aspect('equal');save(f,2,7,'coupon-study','Drilled-bore coupon generated and mesh-checked for later measured fit tests.')
# 3. Return
f,ax=fig('01 / Return-route plan','Actual track centre positions; arrows indicate intended gravity direction only.')
for t,c in zip(D['tracks'],COL):
 s,e=np.array(t['start']),np.array(t['end']);ax.annotate('',xy=e[:2],xytext=s[:2],arrowprops={'arrowstyle':'->','lw':5,'color':c});ax.text(*(s[:2]+e[:2])/2,t['name'],fontsize=12)
for k in ['inlet_mouth','outlet_end']:
 p=D['interfaces'][k];ax.scatter(p[0],p[1],s=140,color=INK);ax.annotate(k.replace('_',' '),(p[0],p[1]),xytext=(4,9),textcoords='offset points')
ax.set(xlim=(-55,125),ylim=(-85,60),xlabel='World X (mm)',ylabel='World Y (mm)');ax.set_aspect('equal');ax.grid();save(f,3,1,'route-plan','Three source-defined return segments and lift interfaces.')
f,ax=fig('02 / Track grade and discrete drops','Each straight falls; that alone does not prove cup-to-cup transfer.')
offset=0
for t,c in zip(D['tracks'],COL):
 ax.plot([offset,offset+t['length_mm']],[t['start'][2],t['end'][2]],color=c,lw=5,label=f"{t['name']}: {t['grade_deg']:.1f}°")
 offset+=t['length_mm']
ax.set(xlabel='Cumulative straight-track length (mm)',ylabel='Track sole reference height (mm)');ax.grid();ax.legend();save(f,3,2,'grade-profile','Computed lengths, downward grades and vertical discontinuities.')
for i,t in enumerate(D['transfers']):
 f,ax=fig(f'{i+3:02d} / Corner {i+1}: ideal trajectory screen','No-wall-hit projectile from isolated solid-sphere rolling speed. Actual rims may intercept it.')
 launch=np.array(t['launch']);target=np.array(t['catch_target']);incoming=D['tracks'][i];unit=np.array(incoming['unit']);speed=incoming['isolated_ideal_speed_mm_s'];time=t['nominal_flight_ms']/1000;ts=np.linspace(0,time,70)
 traj=np.array([launch+unit*speed*x+np.array([0,0,-.5*9810*x*x]) for x in ts]);direction=unit[:2]/np.linalg.norm(unit[:2]);x=(traj[:,:2]-target[:2])@direction
 ax.plot(x,traj[:,2],color=COL[0],lw=3,label='Ideal trajectory');ax.axhline(target[2],color=MUTED,ls='--');ax.axvspan(-4.5,4.5,color=COL[1],alpha=.22,label='Nominal centre-safe cup span');ax.scatter([0],[target[2]],s=90,color=INK)
 ax.set(xlabel='Horizontal travel relative to catch centre (mm)',ylabel='Ball-centre height (mm)');ax.text(.04,.90,f"Projected miss: {t['center_miss_mm']:.1f} mm\nA risk flag, not a proven escape.",transform=ax.transAxes,fontsize=14);ax.legend(loc='lower left');ax.grid();save(f,3,i+3,f'corner-{i+1}-screen','Idealised corner-transfer screen with explicit model limitations.')
f,ax=fig('05 / Catch sensitivity to incoming speed','Assumes no rim collision or friction; nominal safe centre radius = 4.5 mm.')
for t in D['transfers']:
 ax.plot([s['speed_factor'] for s in t['samples']],[s['miss_distance_mm'] for s in t['samples']],label=t['name'],lw=3)
ax.axhline(4.5,color='#d24d4d',ls='--',label='Cup centre-safe radius');ax.set(xlabel='Fraction of isolated-track ideal speed',ylabel='Planar distance from catch centre (mm)');ax.legend();ax.grid();save(f,3,5,'capture-envelope','Velocity sensitivity demonstrates need for physical cup-transfer tests or deeper catcher redesign.')
f,ax=fig('06 / Final-return sweep: funnel interference','3.98 mm sphere on the track centreline and its straight extension past 1.00; no dynamics.')
a=D['return_funnel']['samples'];ax.plot([x['fraction'] for x in a],[x['funnel_overlap_mm3'] for x in a],lw=3,color='#d24d4d');ax.axvline(1,color=INK,ls='--',label='Track endpoint');ax.set(xlabel='Position as fraction of final track length',ylabel='Sphere–funnel overlap (mm³)');ax.grid();ax.legend();ax.text(.03,.9,f"Max overlap: {D['return_funnel']['max_overlap']:.2f} mm³",transform=ax.transAxes,fontsize=15);save(f,3,6,'funnel-collision','New measured centreline collision: earlier straight-segment samples omitted this interface.')
f,ax=fig('07 / Funnel lip: two candidate relief studies','Separate study files only—not merged into the machine or physically validated.')
for data,label,col in [(R,'Original funnel', '#d24d4d'),(R1,'First relief',COL[0]),(R,'Extended relief',COL[1])]:
 key='before_overlap_mm3' if label=='Original funnel' else 'after_overlap_mm3';ax.plot([x['fraction'] for x in data['path']],[x[key] for x in data['path']],lw=3,label=label,color=col)
ax.text(.03,.83,f"Extended relief removed {R['removed_mm3']:.2f} mm³\nMax sampled residual: {R['max_after_overlap_mm3']:.3f} mm³\nWall strength and ball retention still untested.",transform=ax.transAxes,fontsize=13);ax.set(xlabel='Position along final track / track length',ylabel='Overlap (mm³)');ax.legend();ax.grid();save(f,3,7,'relief-comparison','Two executed solid-cut candidates, preserved failed first study and passing second sampled clearance.')
# 4. Manufacturing/validation audit
m=D['existing_checks']['mesh-checks.json'];s=D['existing_checks']['slicing-checks.json'];parts=m['parts']
f,ax=fig('01 / Print-part audit inventory','Published baseline mesh reports, re-read for this review; not another manufacturing event.')
names=[p['name'] for p in parts];ax.set_axis_off();rows=[]
for p in parts:rows.append([p['name'],'yes' if p['watertight'] else 'NO',str(p['components']), 'yes' if p['bed_contact'] else 'NO'])
table=ax.table(cellText=rows,colLabels=['Part','Watertight','Bodies','On bed'],loc='center',cellLoc='left',colWidths=[.56,.16,.12,.16]);table.auto_set_font_size(False);table.set_fontsize(10);table.scale(1,1.5);save(f,4,1,'part-inventory','21 individual published part checks; each expected one solid.')
f,ax=fig('02 / Bed-envelope audit by part','Maximum X/Y extent and height; axis-aligned geometry only, excluding brim/support.')
f.subplots_adjust(left=.27)
ordered=sorted(parts,key=lambda p:max(p['dimensions_mm'][:2]),reverse=True)
y=np.arange(len(ordered));xy=[max(p['dimensions_mm'][:2]) for p in ordered];height=[p['dimensions_mm'][2] for p in ordered]
ax.barh(y-.18,xy,height=.34,color=COL[1],label='Maximum X/Y footprint extent');ax.barh(y+.18,height,height=.34,color=COL[0],label='Print height')
ax.set_yticks(y,[p['name'] for p in ordered]);ax.tick_params(axis='y',labelsize=9);ax.invert_yaxis();ax.axvline(256,color=INK,ls='--',label='256 mm envelope');ax.set(xlim=(0,278),xlabel='Extent (mm)');ax.grid(axis='x');ax.legend(fontsize=10)
save(f,4,2,'bed-fit','All 21 source mesh bounds compared with 256mm envelope; footprint and height separate.')
f,ax=fig('03 / Material demand is concentrated','Existing slicer filament volume includes its generic support/brim choices.')
a=sorted(s['results'],key=lambda p:p['filament_cm3'],reverse=True);bars(ax,[p['name'] for p in a],[p['filament_cm3'] for p in a],'Filament volume (cm³)',COL[1]);ax.tick_params(axis='y',labelsize=9);save(f,4,3,'material-breakdown','Per-part slicer filament requirements, not solid-CAD volumes.')
import re
def minutes(txt):return sum(int(n)*{'h':60,'m':1,'s':1/60}[u] for n,u in re.findall(r'(\d+)([hms])',txt))
f,ax=fig('04 / Printing time is not design time','Generic profile estimates. These values must not be logged as participant work hours.')
a=sorted(s['results'],key=lambda p:minutes(p['estimated_time']),reverse=True);bars(ax,[p['name'] for p in a],[minutes(p['estimated_time'])/60 for p in a],'Estimated print time (hours)',COL[0]);ax.tick_params(axis='y',labelsize=9);save(f,4,4,'print-time','Existing slicer machine-time estimates explicitly separated from human work.')
f,ax=fig('05 / Tall parts deserve a separate print plan','Height/footprint screening from exports—not a measured adhesion or stability test.')
selected=sorted(parts,key=lambda p:p['dimensions_mm'][2],reverse=True)[:9];
for i,p in enumerate(selected):
 x,y,z=p['dimensions_mm'];ax.add_patch(Rectangle((i*33,0),min(x,y),z,facecolor=COL[i%4],alpha=.75));ax.text(i*33+3,z+4,p['name'].replace('-','\n'),fontsize=9,rotation=0)
ax.set(xlim=(-5,320),ylim=(0,170),xlabel='Separated footprints for comparison (not a packed plate)',ylabel='Print height (mm)');ax.grid(axis='y');save(f,4,5,'orientation-risks','Source dimensions identify tall supports/shaft; angled faces and nut traps still need layer review.')
f,ax=fig('06 / Verification coverage, not blanket “PASS”','A clear export can coexist with an unfinished mechanism.')
rows=[('Solid/mesh export','Passed baseline checks'),('STEP round trip','Passed baseline checks'),('Static assembly clashes','Passed at reporting threshold'),('Crank motion samples','Fresh 5° sample audit'),('Indexed bore path','Fresh clear centreline'),('Return-to-funnel path','Collision found; relief candidate'),('Corner transfer dynamics','Ideal screening only'),('Printing / support removal','Not tested physically'),('Continuous marble circulation','Not tested physically')]
ax.set_axis_off()
for i,(name,status) in enumerate(rows):
 y=.94-i*.098;ax.text(.01,y,name,fontsize=14,va='center');ax.text(.53,y,status,fontsize=13,va='center',color=COL[1] if i<5 else '#b45f28');ax.axhline(y-.038,color='#dae2e8')
save(f,4,6,'coverage-matrix','Evidence matrix distinguishes past export validation, fresh audit and remaining physical gates.')
f,ax=fig('07 / Physical test acceptance sequence','Prospective test plan; no check boxes are being marked complete.')
steps=[('1. Measure','Actual ball diameter, shaft and coupon fit'),('2. Empty rotation','No rub, retained bolts, no pinch access'),('3. Load one ball','Stationary index first, then slow hand turn'),('4. Discharge','Release at top without forcing or jamming'),('5. Test each corner','Catch, drain, no bounce or reverse slope'),('6. Return to funnel','Review candidate lip geometry after printing'),('7. Repeat whole cycle','Record observed successes AND failures')]
ax.set_axis_off()
for i,(a,txt) in enumerate(steps):
 y=.94-i*.135;ax.text(.02,y,a,fontsize=16,fontweight='bold');ax.text(.30,y,txt,fontsize=13)
 if i<6:ax.annotate('',xy=(.10,y-.09),xytext=(.10,y-.025),xycoords='axes fraction',arrowprops={'arrowstyle':'->','color':COL[1]})
save(f,4,7,'physical-test-plan','Unexecuted acceptance plan is explicitly prospective, not fabricated test evidence.')
assert len(manifest)==28 and all(sum(m['pack']==i for m in manifest)==7 for i in [1,2,3,4])
(ROOT/'image-manifest.json').write_text(json.dumps(manifest,indent=2))
# Labeled contact sheets are review aids, not counted as evidence images.
review=ROOT/'review';review.mkdir(exist_ok=True)
for group in [1,2,3,4]:
 files=[ROOT/m['image'] for m in manifest if m['pack']==group];sheet=Image.new('RGB',(1600,1050),'#cbd7df');draw=ImageDraw.Draw(sheet)
 for i,p in enumerate(files):
  im=ImageOps.contain(Image.open(p).convert('RGB'),(520,320));x=(i%3)*533;y=(i//3)*350;sheet.paste(im,(x,y));draw.text((x+10,y+322),p.name,fill='black')
 sheet.save(review/f'pack-{group:02d}-overview.jpg',quality=94)
print(json.dumps({'evidence_images':len(manifest),'per_pack':{i:sum(m['pack']==i for m in manifest) for i in [1,2,3,4]}},indent=2))
