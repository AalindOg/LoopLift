#!/usr/bin/env python3
"""Original deterministic electro score used by the LoopLift reels."""
from pathlib import Path
import wave
import numpy as np
a=Path(__file__).resolve().parent
sr=44100; t=np.arange(sr*18)/sr;y=np.zeros(len(t));rng=np.random.default_rng(23)
# Original 120 BPM electro groove: kick, snare, hats, bass and stabs.
for k,start in enumerate(np.arange(0,18,.5)):
    z=t-start;m=(z>=0)&(z<.45);u=z[m]
    y[m]+=.38*np.sin(2*np.pi*(47*u+3.8*(1-np.exp(-u*40))))*np.exp(-u*15)
    if k%2:y[m]+=.13*rng.normal(size=len(u))*np.exp(-u*22)+.06*np.sin(2*np.pi*170*u)*np.exp(-u*28)
    f=[65.406,65.406,77.782,58.27][(k//4)%4]
    y[m]+=.11*(np.sin(2*np.pi*f*u)+.3*np.sin(2*np.pi*2*f*u))*np.minimum(u*100,1)*np.exp(-u*8)
for k,start in enumerate(np.arange(0,18,.25)):
    z=t-start;m=(z>=0)&(z<.09);u=z[m];noise=rng.normal(size=len(u));noise=np.r_[0,np.diff(noise)]
    y[m]+=.023*noise*np.exp(-u*65)
    if k%2==0:
        f=[523.25,622.25,783.99,932.33][(k//2)%4];y[m]+=.046*np.sin(2*np.pi*f*u)*np.exp(-u*19)
for start in [0,2,4,6,7.5,9,10.5,12,13.5,16]:
    z=t-start;m=(z>=0)&(z<.25);u=z[m];y[m]+=.045*rng.normal(size=len(u))*np.exp(-u*17)
y=np.tanh(y*1.4)*.78*np.minimum(np.clip(t/.018,0,1),np.clip((18-t)/.25,0,1))
st=np.stack([y,.98*y+.014*np.roll(y,280)],1)
with wave.open(str(a/'beat.wav'),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr);f.writeframes((st*32767).astype('<i2').tobytes())
