#!/usr/bin/env python3
"""Stage only the final, verified build for GitHub; hash all release files."""
from pathlib import Path
import json,hashlib,shutil,zipfile
ROOT=Path(__file__).resolve().parents[1]
id=json.loads((ROOT/'build/latest.json').read_text())['build_id'];out=ROOT/'build'/id
geo=json.loads((out/'geometry-checks.json').read_text());mesh=json.loads((out/'mesh-checks.json').read_text());paths=json.loads((out/'path-checks.json').read_text());slices=json.loads((out/'slicing-checks.json').read_text())
assert geo['build_id']==mesh['build_id']==paths['build_id']==slices['build_id']==id
assert not geo['clashes'] and not geo['errors'] and not geo['rotor_envelope_clashes']
assert mesh['all_meshes_pass'] and mesh['step_valid'] and mesh['step_volume_relative_error']<1e-5
assert paths['passed_nominal_samples'] and slices['all_pass']
for src,dst in [('parts','parts'),('assembly-parts','assembly-parts'),('images','images')]:
 shutil.copytree(out/src,ROOT/dst,dirs_exist_ok=True)
(ROOT/'checks').mkdir(exist_ok=True);(ROOT/'exports').mkdir(exist_ok=True)
for name in ['geometry-checks.json','mesh-checks.json','path-checks.json','slicing-checks.json','inventory.json']:shutil.copy2(out/name,ROOT/'checks'/name)
for name in ['LoopLift.step','LoopLift.glb']:shutil.copy2(out/name,ROOT/'exports'/name)
# All source, docs and final exports; never interim build directories or slicer G-code.
files=[]
for folder in ['cad','parts','assembly-parts','images','checks','exports','upstream']:
 files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
files.extend(p for p in ROOT.iterdir() if p.is_file() and p.name not in ['MANIFEST.json'] and not p.name.endswith('.zip') and not p.name.endswith('.log'))
files=sorted(set(files));manifest={'build_id':id,'files':{str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files}}
(ROOT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2))
zipout=ROOT.parent/'LoopLift-v0.1-design-prototype.zip'
with zipfile.ZipFile(zipout,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files+[ROOT/'MANIFEST.json']:z.write(p,'LoopLift/'+str(p.relative_to(ROOT)))
with zipfile.ZipFile(zipout) as z:
 assert z.testzip() is None
 for rel,meta in manifest['files'].items():assert hashlib.sha256(z.read('LoopLift/'+rel)).hexdigest()==meta['sha256']
print(json.dumps({'build_id':id,'release_files':len(files)+1,'print_stls':len(list((ROOT/'parts').glob('*.stl'))),'archive':str(zipout),'bytes':zipout.stat().st_size},indent=2))
