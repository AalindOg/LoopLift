#!/usr/bin/env python3
"""Text-free LoopLift CAD idea reel. Camera motion only; NOT a physics demo."""
from pathlib import Path
import json, math, subprocess
import vtk
from vtk.util.numpy_support import vtk_to_numpy
from PIL import Image

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
INV=json.loads((PROJECT/'checks/inventory.json').read_text())
W,H,FPS,SECONDS=720,1280,24,32
ren=vtk.vtkRenderer();ren.SetBackground(.945,.957,.967)
win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(W,H)
win.SetMultiSamples(4);win.AddRenderer(ren)
actors={}
for p in INV['parts']:
    if p['name'] in ['clearance-coupon','marble-8mm']:continue
    reader=vtk.vtkSTLReader();reader.SetFileName(str(PROJECT/'assembly-parts'/(p['name']+'.stl')))
    normals=vtk.vtkPolyDataNormals();normals.SetInputConnection(reader.GetOutputPort());normals.SetFeatureAngle(45);normals.ConsistencyOn();normals.AutoOrientNormalsOn()
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort())
    a=vtk.vtkActor();a.SetMapper(mapper)
    prop=a.GetProperty();prop.SetColor(*p['color']);prop.SetInterpolationToPhong()
    prop.SetAmbient(.3);prop.SetDiffuse(.75);prop.SetSpecular(.24);prop.SetSpecularPower(30)
    ren.AddActor(a);actors[p['name']]=a
ren.AutomaticLightCreationOff()
for pos,intensity in [((-300,-450,500),.85),((450,-50,350),.55),((50,450,350),.55)]:
    light=vtk.vtkLight();light.SetPosition(*pos);light.SetFocalPoint(0,0,90);light.SetIntensity(intensity);ren.AddLight(light)
cam=ren.GetActiveCamera();cam.ParallelProjectionOn();cam.SetViewUp(0,0,1)
cutaway=['front-guard','crank-arm','crank-knob','shaft-retainer','front-spacer']
# Individual real-model views. No overlays, new labels, voices, or animated marble.
shots=[
    dict(start=0,end=8,mode='full',target=(-7,-3,83),azimuth=(-62,-118),height=(330,340),scale=(253,253)),
    dict(start=8,end=15,mode='cutaway',target=(-17,0,101),azimuth=(-70,-110),height=(310,340),scale=(192,182)),
    dict(start=15,end=21,mode='tracks',target=(41,-15,104),azimuth=(-36,12),height=(470,440),scale=(146,150)),
    dict(start=21,end=26,mode='rotor',target=(-30,0,105),azimuth=(-80,-110),height=(235,295),scale=(152,149)),
    dict(start=26,end=32,mode='full',target=(-7,-3,83),azimuth=(-60,-90),height=(360,320),scale=(253,253)),
]
silent=ROOT/'looplift-silent.mp4'
proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(silent)],stdin=subprocess.PIPE)
grab=vtk.vtkWindowToImageFilter();grab.SetInput(win);grab.SetInputBufferTypeToRGB();grab.ReadFrontBufferOff()
frames=0
try:
    for shot in shots:
        for name,a in actors.items():
            visible=True
            if shot['mode']=='cutaway' and name in cutaway:visible=False
            if shot['mode']=='rotor':visible=name in ['eight-pocket-rotor','rear-guard','keyed-shaft','rear-bush','inlet-funnel','outlet-sleeve']
            a.SetVisibility(visible)
        length=round((shot['end']-shot['start'])*FPS)
        for n in range(length):
            f=n/max(1,length-1);e=(1-math.cos(math.pi*f))/2
            az=math.radians(shot['azimuth'][0]+e*(shot['azimuth'][1]-shot['azimuth'][0]))
            target=shot['target'];cam.SetFocalPoint(*target)
            cam.SetPosition(target[0]+650*math.cos(az),target[1]+650*math.sin(az),shot['height'][0]+e*(shot['height'][1]-shot['height'][0]))
            cam.SetParallelScale(shot['scale'][0]+e*(shot['scale'][1]-shot['scale'][0]))
            ren.ResetCameraClippingRange();win.Render();grab.Modified();grab.Update()
            image=grab.GetOutput();arr=vtk_to_numpy(image.GetPointData().GetScalars()).reshape(H,W,3)[::-1].copy()
            proc.stdin.write(arr.tobytes());frames+=1
        print(shot['mode'],shot['start'],shot['end'],'rendered',flush=True)
finally:proc.stdin.close()
assert proc.wait()==0 and frames==FPS*SECONDS
out=ROOT/'LoopLift-idea-reel-no-text.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(silent),'-stream_loop','-1','-i',str(ROOT.parent/'assets/beat.wav'),'-map','0:v:0','-map','1:a:0','-t',str(SECONDS),'-c:v','copy','-af','volume=0.22,afade=t=in:st=0:d=0.5,afade=t=out:st=30.5:d=1.5','-c:a','aac','-b:a','128k','-movflags','+faststart',str(out)],check=True)
subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_entries','format=duration,size:stream=codec_name,width,height,r_frame_rate,nb_read_frames','-of','json',str(out)]))
assert float(probe['format']['duration'])>=30 and float(probe['format']['duration'])<=60
assert probe['streams'][0]['nb_read_frames']==str(frames)
qa=ROOT/'qa';qa.mkdir(exist_ok=True)
frames_to_sample=[24,168,216,336,384,480,528,600,648,744]
selector='+'.join(f'eq(n\\,{n})' for n in frames_to_sample)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(out),'-vf',f'select={selector},scale=216:384','-vsync','0',str(qa/'frame-%02d.png')],check=True)
imgs=sorted(qa.glob('frame-*.png'));assert len(imgs)==len(frames_to_sample)
contact=Image.new('RGB',(5*224,2*392),'#87929d')
for i,p in enumerate(imgs):contact.paste(Image.open(p),((i%5)*224+4,(i//5)*392+4))
contact.save(ROOT/'contact-sheet.jpg',quality=95)
(ROOT/'validation.json').write_text(json.dumps({'probe':probe,'build_id':INV['build_id'],'shots':shots,'added_text':False,'narration':False,'motion':'camera orbit only; static CAD, not a working-device or dynamics demonstration','full_decode':'passed'},indent=2))
print(json.dumps(probe,indent=2),flush=True)
print(out,flush=True)
