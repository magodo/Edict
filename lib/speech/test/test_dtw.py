#!/bin/env python
# -*- coding: utf-8 -*-

#########################################################################
# Author: Zhaoting Weng
# Created Time: Thu 04 Dec 2014 12:20:24 AM CST
# File Name: example.py
# Description:
#########################################################################

from edict.speech import waveio
import numpy as np
from edict.speech import dtw
from edict.speech import mfcc

# Get signal from .wav file
signal1, FS = waveio.wave_from_file("/home/magodo/code/voiceMaterial/1b.wav")
signal2, FS = waveio.wave_from_file("/home/magodo/code/voiceMaterial/7b.wav")
# MFCC
temp1 = mfcc.mfcc(signal1, FS, endpoint = True, appendEnergy = True)
temp2 = mfcc.mfcc(signal2, FS, endpoint = True, appendEnergy = True)
# DTW
score = dtw.dtw(temp1, temp2)

print score
