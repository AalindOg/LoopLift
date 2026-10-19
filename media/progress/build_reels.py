#!/usr/bin/env python3
"""Four actual-CAD/evidence progress reels. No overlays, hour claims or simulated operation."""
from pathlib import Path
import argparse,hashlib,itertools,json,math,subprocess,sys
import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
PACKS=PROJECT/'evidence'
MUSIC=ROOT.parent/'assets/beat.wav'
INV=json.loads((PROJECT/'checks/inventory.json').read_text())
AUDIT=json.loads((PACKS/'audit-results.json').read_text())
assert INV['build_id']==AUDIT['build_id']
assert hashlib.sha256((PROJECT/'cad/build.py').read_bytes()+(PROJECT/'cad/track_profile.py').read_bytes()).hexdigest()[:12]==INV['build_id']
EVIDENCE=json.loads((PACKS/'image-manifest.json').read_text())
W,H,FPS=720,1280,24
BG=(241,244,247)
PARTS={p['name']:p for p in INV['parts'] if p['name']!='marble-8mm'}
ALL=[n for n in PARTS if n!='clearance-coupon']
LIFT=['rear-guard','eight-pocket-rotor','keyed-shaft','rear-bush','inlet-funnel','outlet-sleeve']
DRIVE=['keyed-shaft','rear-bush','front-spacer','crank-arm','crank-knob','shaft-retainer']
TRACKS=['upper-return','side-return','lower-return','inlet-funnel','outlet-sleeve']
TOPICS={1:'feed-discharge',2:'drive-tolerances',3:'return-path',4:'print-preparation'}
# Each evidence frame has its source chart below an actual, static CAD view.
SETS={
1:[(LIFT,-74,-54,0.6),(['front-guard','inlet-funnel'],-78,-56,.65),(['front-guard','eight-pocket-rotor','inlet-funnel'],-76,-62,.5),(['rear-guard','outlet-sleeve'],80,104,.65),(['rear-guard','outlet-sleeve','eight-pocket-rotor'],95,112,.45),(['eight-pocket-rotor','keyed-shaft'],-90,-70,.5),(LIFT,-48,-24,.85)],
2:[(DRIVE,-65,-40,.7),(['keyed-shaft','crank-arm'],-70,-40,.8),(['keyed-shaft','rear-bush'],75,102,.65),(['crank-arm','crank-knob','front-guard','inlet-funnel'],-65,-43,.5),(['eight-pocket-rotor'],-80,-58,.6),(['front-guard','rear-guard','eight-pocket-rotor'],-8,10,.55),(['study-coupon'],-80,-52,.9)],
3:[(TRACKS,-65,-40,1.65),(TRACKS,-78,-54,.45),(['upper-return','side-return'],-58,-34,1.8),(['side-return','lower-return'],-65,-42,1.75),(['upper-return','side-return','lower-return'],-45,-20,1.4),(['lower-return','inlet-funnel'],-65,-40,1.15),(['funnel-before','funnel-after'],-70,-35,1.7)],
4:[(['print:rear-guard','print:front-guard','print:eight-pocket-rotor','print:crank-arm'],-75,-55,1.35),(['print:baseplate'],-72,-55,1.1),(['print:baseplate','print:eight-pocket-rotor'],-72,-52,1.2),(['print:eight-pocket-rotor','print:rear-guard'],-65,-45,1.5),(['print:upper-return-stand','print:side-return-stand','print:lower-return-stand'],-70,-40,.6),(['study-coupon','print:keyed-shaft','print:rear-bush'],-70,-45,1.2),(ALL,-60,-40,.75)]}

def prepare():
 import cadquery as cq
 dest=ROOT/'assets';dest.mkdir(exist_ok=True)
 source=PACKS/'study-parts/funnel-lip-relief-study.step'
 cq.exporters.export(cq.importers.importStep(str(source)),str(dest/'funnel-relief-world.stl'))
 print('Prepared actual STEP candidate for matched-orientation comparison',flush=True)

class Renderer:
 def __init__(self):
  self.ren=vtk.vtkRenderer();self.ren.SetBackground(*(v/255 for v in BG))
  self.win=vtk.vtkRenderWindow();self.win.SetOffScreenRendering(1);self.win.SetMultiSamples(4);self.win.AddRenderer(self.ren)
  self.actors={};self.sources={}
  for name,p in PARTS.items():self.add(name,PROJECT/'assembly-parts'/f'{name}.stl',p['color'])
  for n,p in PARTS.items():self.add('print:'+n,PROJECT/'parts'/f'{n}.stl',p['color'])
  self.add('study-coupon',PACKS/'study-parts/expanded-clearance-coupon.stl',(.52,.69,.78))
  self.add('funnel-before',PROJECT/'assembly-parts/inlet-funnel.stl',(.99,.47,.17))
  self.add('funnel-after',ROOT/'assets/funnel-relief-world.stl',(.2,.69,.69))
  self.ren.AutomaticLightCreationOff();self.lights=[]
  for xyz,intensity in [((-300,-450,600),.85),((450,-50,350),.6),((50,450,400),.6)]:
   light=vtk.vtkLight();light.SetPosition(*xyz);light.SetIntensity(intensity);self.ren.AddLight(light);self.lights.append(light)
  self.cam=self.ren.GetActiveCamera();self.cam.ParallelProjectionOn();self.cam.SetViewUp(0,0,1)
  self.grab=vtk.vtkWindowToImageFilter();self.grab.SetInput(self.win);self.grab.SetInputBufferTypeToRGB();self.grab.ReadFrontBufferOff()
 def add(self,name,path,color):
  assert path.is_file(),path
  reader=vtk.vtkSTLReader();reader.SetFileName(str(path));reader.Update();assert reader.GetOutput().GetNumberOfPoints()>0
  normals=vtk.vtkPolyDataNormals();normals.SetInputConnection(reader.GetOutputPort());normals.SetFeatureAngle(45);normals.ConsistencyOn();normals.AutoOrientNormalsOn()
  mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort());a=vtk.vtkActor();a.SetMapper(mapper)
  prop=a.GetProperty();prop.SetColor(*color);prop.SetInterpolationToPhong();prop.SetAmbient(.3);prop.SetDiffuse(.75);prop.SetSpecular(.22);prop.SetSpecularPower(30)
  self.ren.AddActor(a);self.actors[name]=a;self.sources[name]=str(path);a.SetVisibility(False)
 def setup(self,shot):
  chosen=shot['parts'];height=H if shot['kind']=='full' else 800
  self.win.SetSize(W,height)
  for n,a in self.actors.items():a.SetPosition(0,0,0);a.SetVisibility(n in chosen)
  # Study parts/print exports are laid out as separate objects, never installed as approved parts.
  layout=all(n.startswith('print:') or n in ['study-coupon','funnel-before','funnel-after'] for n in chosen)
  if layout:
   cursor=0
   for n in chosen:
    a=self.actors[n];bb=a.GetBounds();width=bb[1]-bb[0]
    a.SetPosition(cursor-bb[0],-(bb[2]+bb[3])/2,-bb[4]);cursor+=width+12
  bounds=np.array([self.actors[n].GetBounds() for n in chosen]);lo=bounds[:,[0,2,4]].min(axis=0);hi=bounds[:,[1,3,5]].max(axis=0)
  center=(lo+hi)/2;corners=np.array(list(itertools.product(*zip(lo,hi))))-center
  # Conservative maximum projected bounding box across every orbit, fitted to portrait aspect.
  scales=[]
  for u in np.linspace(0,1,31):
   az=math.radians(shot['azimuth'][0]+u*(shot['azimuth'][1]-shot['azimuth'][0]));direction=np.array([math.cos(az),math.sin(az),shot['elevation']]);direction/=np.linalg.norm(direction)
   right=np.cross([0,0,1],direction);right/=np.linalg.norm(right);up=np.cross(direction,right)
   scales.append(max(np.abs(corners@up).max(),np.abs(corners@right).max()/(W/height))*1.105)
  shot['computed_scale']=float(max(scales));shot['target']=center.tolist();shot['render_height']=height
  for light in self.lights:light.SetFocalPoint(*center)
  self.current=shot
 def frame(self,u):
  shot=self.current;ease=(1-math.cos(math.pi*u))/2;az=math.radians(shot['azimuth'][0]+ease*(shot['azimuth'][1]-shot['azimuth'][0]));target=np.array(shot['target'])
  self.cam.SetFocalPoint(*target);self.cam.SetPosition(*(target+np.array([650*math.cos(az),650*math.sin(az),650*shot['elevation']])));self.cam.SetParallelScale(shot['computed_scale'])
  self.ren.ResetCameraClippingRange();self.win.Render();self.grab.Modified();self.grab.Update()
  arr=vtk_to_numpy(self.grab.GetOutput().GetPointData().GetScalars()).reshape(shot['render_height'],W,3)[::-1].copy()
  frame=Image.new('RGB',(W,H),BG);frame.paste(Image.fromarray(arr),(0,0))
  if shot['kind']=='evidence':
   image=ImageOps.contain(Image.open(shot['evidence']).convert('RGB'),(700,450),Image.Resampling.LANCZOS)
   frame.paste(image,((W-image.width)//2,810+(450-image.height)//2))
  return frame

def shots_for(pack):
 images=[x for x in EVIDENCE if x['pack']==pack];assert len(images)==7
 shots=[dict(kind='full',duration=4,parts=ALL,azimuth=[-67,-49],elevation=.58)]
 for i,(names,a,z,elev) in enumerate(SETS[pack]):
  shots.append(dict(kind='evidence',duration=5,parts=names,azimuth=[a,z],elevation=elev,evidence=str(PACKS/images[i]['image']),evidence_description=images[i]['evidence']))
 shots.append(dict(kind='full',duration=4,parts=ALL,azimuth=[-45,-65],elevation=.75))
 assert sum(s['duration'] for s in shots)==43
 return shots

def save_sheet(frames,path):
 sheet=Image.new('RGB',(5*224,math.ceil(len(frames)/5)*414),'#7e8a96');d=ImageDraw.Draw(sheet)
 for i,(label,im) in enumerate(frames):
  im=ImageOps.contain(im,(216,384));x=i%5*224+4;y=i//5*414+4;sheet.paste(im,(x,y));d.text((x,y+387),label,fill='white')
 sheet.save(path,quality=93)

def run(pack,preview=False):
 folder=ROOT/f'reel-{pack:02d}';folder.mkdir(exist_ok=True)
 r=Renderer();shots=shots_for(pack);frames=[]
 for i,shot in enumerate(shots):
  r.setup(shot)
  for u in [0,.5,1]:frames.append((f'Shot {i+1} / {u:g}',r.frame(u)))
 save_sheet(frames,folder/'preview.jpg')
 (folder/'shot-contract.json').write_text(json.dumps({'pack':pack,'source_commit':AUDIT['source_commit'],'build_id':INV['build_id'],'duration_seconds':sum(s['duration'] for s in shots),'shots':shots,'part_sources':r.sources,'human_hours':None,'physical_tested':False,'platform_progress_modal_inspected':False,'format_basis':'43-second portrait editorial default; current progress-modal requirements not supplied','assistance':'AI-assisted rendering and analysis','music':'Existing original procedural electro score; media/assets/make_music.py','added_text':False,'original_evidence_labels_preserved':True},indent=2))
 if preview:print('Preview',pack,folder/'preview.jpg',flush=True);return
 silent=folder/'silent.mp4';totalframes=FPS*sum(s['duration'] for s in shots)
 cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','19','-pix_fmt','yuv420p',str(silent)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 count=0
 try:
  for i,shot in enumerate(shots):
   r.setup(shot);n=FPS*shot['duration']
   for k in range(n):proc.stdin.write(r.frame(k/max(1,n-1)).tobytes());count+=1
   print(f'Pack {pack}, shot {i+1}/{len(shots)} rendered',flush=True)
 finally:proc.stdin.close()
 assert proc.wait()==0 and count==totalframes
 duration=sum(s['duration'] for s in shots);out=ROOT/f'LoopLift-progress-{pack:02d}-{TOPICS[pack]}.mp4'
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(silent),'-stream_loop','-1','-i',str(MUSIC),'-map','0:v:0','-map','1:a:0','-t',str(duration),'-c:v','copy','-af',f'volume=0.4,afade=t=in:st=0:d=0.5,afade=t=out:st={duration-1.5}:d=1.5','-c:a','aac','-b:a','128k','-movflags','+faststart',str(out)],check=True)
 subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_entries','format=duration,size:stream=codec_name,width,height,r_frame_rate,nb_read_frames','-of','json',str(out)]))
 video=next(s for s in probe['streams'] if s['codec_name']=='h264');assert video['width']==W and video['height']==H and int(video['nb_read_frames'])==count
 assert abs(float(probe['format']['duration'])-duration)<.1 and any(s['codec_name']=='aac' for s in probe['streams'])
 qa=folder/'decoded';qa.mkdir(exist_ok=True);times=[.0,2,3.9]+[4+i*5+2.5 for i in range(7)]+[39.1,41,42.9]
 actual=[]
 for i,t in enumerate(times):
  p=qa/f'{i+1:02d}.jpg';subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(out),'-frames:v','1','-q:v','2',str(p)],check=True);actual.append((f'{t:.1f}s',Image.open(p).copy()))
 save_sheet(actual,folder/'decoded-contact-sheet.jpg')
 validation={'file':str(out),'probe':probe,'full_decode':'passed','evidence_images':7,'decoded_samples':len(actual),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'human_hours':None,'physical_tested':False,'motion':'Camera only; separate parts laid out for inspection; no operation animation'}
 (folder/'validation.json').write_text(json.dumps(validation,indent=2));print(json.dumps(validation),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');p.add_argument('--preview',action='store_true');p.add_argument('--pack',type=int,choices=[1,2,3,4]);args=p.parse_args()
 if args.prepare:prepare()
 else:run(args.pack,args.preview)
