#!/usr/bin/env python3
"""Render actual exported parts and an explanatory cutaway; no fake simulation."""
from pathlib import Path
import json
import vtk
from PIL import Image,ImageOps,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
id=json.loads((ROOT/'build/latest.json').read_text())['build_id'];out=ROOT/'build'/id
inv=json.loads((out/'inventory.json').read_text());images=out/'images';images.mkdir(exist_ok=True)
ren=vtk.vtkRenderer();ren.SetBackground(.945,.957,.967)
win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(1500,1200);win.SetMultiSamples(8);win.AddRenderer(ren)
actors={}
for p in inv['parts']:
 if p['name']=='clearance-coupon':continue
 r=vtk.vtkSTLReader();r.SetFileName(str(out/'assembly-parts'/(p['name']+'.stl')))
 norm=vtk.vtkPolyDataNormals();norm.SetInputConnection(r.GetOutputPort());norm.SetFeatureAngle(45);norm.AutoOrientNormalsOn();norm.ConsistencyOn()
 m=vtk.vtkPolyDataMapper();m.SetInputConnection(norm.GetOutputPort());a=vtk.vtkActor();a.SetMapper(m)
 prop=a.GetProperty();prop.SetColor(*p['color']);prop.SetInterpolationToPhong();prop.SetAmbient(.3);prop.SetDiffuse(.75);prop.SetSpecular(.25);prop.SetSpecularPower(30)
 ren.AddActor(a);actors[p['name']]=a
ren.AutomaticLightCreationOff()
for pos,intensity in [((-250,-450,500),.8),((500,-50,350),.6),((50,400,350),.6)]:
 l=vtk.vtkLight();l.SetPosition(*pos);l.SetFocalPoint(0,0,85);l.SetIntensity(intensity);ren.AddLight(l)
cam=ren.GetActiveCamera();cam.ParallelProjectionOn();cam.SetViewUp(0,0,1);cam.SetFocalPoint(-5,0,85);cam.SetParallelScale(126)
def render(name,pos):
 cam.SetPosition(*pos);ren.ResetCameraClippingRange();win.Render();f=vtk.vtkWindowToImageFilter();f.SetInput(win);f.SetInputBufferTypeToRGB();f.ReadFrontBufferOff();f.Update();w=vtk.vtkPNGWriter();w.SetFileName(str(images/(name+'.png')));w.SetInputConnection(f.GetOutputPort());w.Write();print(name,flush=True)
render('assembled',(370,-590,380));render('rear',(350,560,330));render('front',(0,-650,170));render('top',(200,-350,680))
actors['front-guard'].SetVisibility(False);actors['crank-arm'].SetVisibility(False);actors['crank-knob'].SetVisibility(False);actors['shaft-retainer'].SetVisibility(False)
render('cutaway',(340,-590,360))
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
board=Image.new('RGB',(2200,1450),'#f1f5f8');d=ImageDraw.Draw(board)
d.text((55,40),'LoopLift',font=ImageFont.truetype(font,62),fill='#173344')
d.text((55,121),'Hand-cranked marble lift + replaceable gravity return',font=ImageFont.truetype(font,28),fill='#4b626f')
for i,(name,label) in enumerate([('assembled','ASSEMBLY'),('cutaway','CUTAWAY / FRONT GUARD HIDDEN')]):
 im=Image.open(images/(name+'.png'));im=ImageOps.contain(im,(1060,960));board.paste(im,(i*1100+20,240));d.text((i*1100+55,1120),label,font=ImageFont.truetype(font,27),fill='#173344')
d.text((55,1240),'8 mm marbles / 8-pocket rotor / 3 bolted track modules',font=ImageFont.truetype(font,29),fill='#173344')
d.text((55,1300),'Geometry + slice checks are not a physical test. Prototype: not yet printed.',font=ImageFont.truetype(font,25),fill='#4b626f')
board.save(images/'hero.jpg',quality=94)
