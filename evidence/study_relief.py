#!/usr/bin/env python3
"""Candidate funnel-lip clearance relief study, separate from published machine.
Removes only the swept clearance envelope near the final track mouth.
Not validated for strength, retention, gravity capture or working flow.
"""
from pathlib import Path
import sys,json,math
import cadquery as cq
import trimesh
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'cad'))
import build as b
start,end=b.ROUTES[-1][1:];L=math.dist(start,end)
funnel=b.pose(b.funnel(True))
a=b.point_track((.75*L,0,6.4),start,end);z=b.point_track((1.15*L,0,6.4),start,end)
v=cq.Vector(*z)-cq.Vector(*a)
cut=cq.Solid.makeCylinder(4.3,v.Length,cq.Vector(*a),v.normalized())
relieved=funnel.cut(cut).val()
assert relieved.isValid() and len(relieved.Solids())==1 and relieved.Volume()>0
before=funnel.val().Volume(1e-7);after=relieved.Volume(1e-7)
path=ROOT/'study-parts';path.mkdir(exist_ok=True)
cq.exporters.export(relieved,str(path/'funnel-lip-relief-study.step'))
# Export true local-axis print orientation.
local=relieved.translate(tuple(-x for x in b.CENTER)).rotate((0,0,0),(1,0,0),-b.TILT)
bb=local.BoundingBox();local=local.translate((-bb.xmin,-bb.ymin,-bb.zmin))
cq.exporters.export(local,str(path/'funnel-lip-relief-study.stl'))
checks=[]
for i in range(36):
 f=.8+i*(1.08-.8)/35;p=b.point_track((f*L,0,6.4),start,end)
 ball=cq.Workplane('XY').sphere(3.98).translate(p).val()
 checks.append({'fraction':f,'before_overlap_mm3':ball.intersect(funnel.val()).Volume(1e-7),'after_overlap_mm3':ball.intersect(relieved).Volume(1e-7)})
meshdata={}
for filename in ['funnel-lip-relief-study.stl','expanded-clearance-coupon.stl']:
 mesh=trimesh.load_mesh(path/filename);meshdata[filename]={'watertight':bool(mesh.is_watertight),'winding':bool(mesh.is_winding_consistent),'connected_components':len(mesh.split()),'positive_volume':bool(mesh.volume>0)}
 assert mesh.is_watertight and mesh.is_winding_consistent and len(mesh.split())==1 and mesh.volume>0
result={'scope':'Candidate geometry relief only; not incorporated in LoopLift or physically tested','before_volume_mm3':before,'after_volume_mm3':after,'removed_mm3':before-after,'path':checks,'max_after_overlap_mm3':max(c['after_overlap_mm3'] for c in checks),'mesh_checks':meshdata,'published_machine_changed':False,'new_risks':['lip wall loss','ball retention','remaining impact dynamics','support removal'],'physical_tested':False}
(ROOT/'relief-results.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='path'},indent=2))
