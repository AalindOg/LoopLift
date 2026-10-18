#!/usr/bin/env python3
"""Verify one frozen LoopLift build. No dynamics or physical-test claim."""
from pathlib import Path
import json,hashlib
import numpy as np
import trimesh
import cadquery as cq
ROOT=Path(__file__).resolve().parents[1]
id=json.loads((ROOT/'build/latest.json').read_text())['build_id'];out=ROOT/'build'/id
inv=json.loads((out/'inventory.json').read_text())
geo=json.loads((out/'geometry-checks.json').read_text())
assert not geo['clashes'] and not geo['errors'] and not geo['rotor_envelope_clashes']
checks=[];scene=trimesh.Scene()
for p in inv['parts']:
 if p['printable']:
  mesh=trimesh.load_mesh(out/'parts'/(p['name']+'.stl'))
  c={'name':p['name'],'watertight':bool(mesh.is_watertight),'winding':bool(mesh.is_winding_consistent),'finite':bool(np.isfinite(mesh.vertices).all()),'positive_volume':bool(mesh.volume>0),'components':len(mesh.split()),'dimensions_mm':mesh.extents.tolist(),'bed_256_fit':bool((mesh.extents<=np.array([256,256,256])).all()),'bed_contact':bool(abs(mesh.bounds[0,2])<1e-4)}
  c['passed']=all(c[k] for k in ['watertight','winding','finite','positive_volume','bed_256_fit','bed_contact']) and c['components']==1;checks.append(c)
 if p['name']!='clearance-coupon':
  mesh=trimesh.load_mesh(out/'assembly-parts'/(p['name']+'.stl'))
  mesh.visual=trimesh.visual.ColorVisuals(mesh,face_colors=[round(x*255) for x in p['color']]+[255]);scene.add_geometry(mesh,node_name=p['name'],geom_name=p['name'])
expected=[p for p in inv['parts'] if p['name']!='clearance-coupon']
step=cq.importers.importStep(str(out/'LoopLift.step')).val(); before=sum(p['volume_mm3'] for p in expected);after=sum(s.Volume(1e-7) for s in step.Solids());error=abs(after-before)/before
scene.apply_transform(trimesh.transformations.rotation_matrix(-np.pi/2,[1,0,0]));scene.apply_scale(.001)
(out/'LoopLift.glb').write_bytes(scene.export(file_type='glb'));loaded=trimesh.load(out/'LoopLift.glb',force='scene')
report={'build_id':id,'printable_parts':len(checks),'all_meshes_pass':all(c['passed'] for c in checks),'step_valid':step.isValid(),'step_solid_count':len(step.Solids()),'expected_step_solids':len(expected),'step_volume_relative_error':error,'glb_geometry_count':len(loaded.geometry),'glb_dimensions_m':loaded.extents.tolist(),'parts':checks,'physical_tested':False}
(out/'mesh-checks.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='parts'},indent=2));print('failed',[c for c in checks if not c['passed']])
assert report['all_meshes_pass'] and report['step_valid'] and len(step.Solids())==len(expected) and error<1e-5 and len(loaded.geometry)==len(expected)
