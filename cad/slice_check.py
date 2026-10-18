#!/usr/bin/env python3
"""Generic slicer smoke test, NOT printer-ready G-code. Temp G-code stays outside repo."""
from pathlib import Path
import os,subprocess,json,re,concurrent.futures
ROOT=Path(__file__).resolve().parents[1]
id=json.loads((ROOT/'build/latest.json').read_text())['build_id'];out=ROOT/'build'/id
slicer=os.environ.get('PRUSA_SLICER','prusa-slicer')
scratch=Path(os.environ['TMPDIR'])/('looplift-slice-'+id);scratch.mkdir(exist_ok=True)
inv=json.loads((out/'inventory.json').read_text());parts=[p for p in inv['parts'] if p['printable']]

def run(p):
 name=p['name'];g=scratch/(name+'.gcode')
 args=[slicer,'--export-gcode','--bed-shape','0x0,256x0,256x256,0x256','--center','128,128','--layer-height','0.2','--first-layer-height','0.2','--nozzle-diameter','0.4','--filament-diameter','1.75','--perimeters','3','--fill-density','20%','--fill-pattern','gyroid','--skirts','0','--brim-width','3','--support-material','--support-material-buildplate-only','--support-material-threshold','45','--threads','2','-o',str(g),str(out/'parts'/(name+'.stl'))]
 proc=subprocess.run(args,capture_output=True,text=True,timeout=180)
 txt=g.read_text(errors='replace') if g.exists() else ''
 mm=re.search(r'; filament used \[mm\] = ([0-9.]+)',txt);cm=re.search(r'; filament used \[cm3\] = ([0-9.]+)',txt);tm=re.search(r'; estimated printing time \(normal mode\) = (.+)',txt)
 warnings=[x for x in (proc.stdout+proc.stderr).splitlines() if any(t in x.lower() for t in ['warning','error','empty','repair'])]
 return {'name':name,'exit_code':proc.returncode,'gcode_bytes':g.stat().st_size if g.exists() else 0,'layer_markers':txt.count(';LAYER_CHANGE'),'filament_mm':float(mm.group(1)) if mm else None,'filament_cm3':float(cm.group(1)) if cm else None,'estimated_time':tm.group(1) if tm else None,'warnings':warnings,'passed':proc.returncode==0 and txt.count(';LAYER_CHANGE')>0}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:results=list(ex.map(run,parts))
report={'build_id':id,'slicer_version':'PrusaSlicer 2.7.2 Ubuntu package','tested_parts':len(results),'all_pass':all(r['passed'] for r in results),'settings':{'bed_mm':[256,256],'layer_mm':.2,'nozzle_mm':.4,'perimeters':3,'infill':'20% gyroid','supports':'buildplate only, 45 degree threshold','brim_mm':3},'results':results,'limitations':'Generic slicing only. No printer-specific G-code published; support removal and physical tolerances remain untested.'}
(out/'slicing-checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert report['all_pass']
