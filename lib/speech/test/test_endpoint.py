#!/bin/env python
# -*- coding: utf-8 -*-

#########################################################################
# Author: Zhaoting Weng
# Created Time: Sat 06 Dec 2014 08:23:54 PM CST
# File Name: test.py
# Description:
#
#       1. Test performance of end-point detection algorithm;
#       2. Test performance of DTW algorithm;
#########################################################################

from edict.speech.preprocess import signal_to_powerspec
from edict.speech.dtw import dtw
from edict.speech.waveio import wave_from_file

file_prefix = "/home/magodo/code/voiceMaterial/"
wave_files = [file_prefix+str(number)+"a.wav" if i is 0 else file_prefix+str(number)+"b.wav" for number in range(10) for i in range(2)]

for wave_file in wave_files:
    print "Processing file: %s" % wave_file
    signal, fs = wave_from_file(wave_file)
    signal_to_powerspec(signal, fs = fs, endpoint = True, show = True)

