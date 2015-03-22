#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################################################
# Author: Zhaoting Weng
# Created Time: Sun 22 Mar 2015 12:09:19 AM CST
# File Name: stream_from_micro.py
# Description:
#########################################################################

from audiostream import get_input

# declare a callback where we'll receive the data
def callback_mic(data):
    print 'i got', len(data)

# get the microphone (or from another source if available)
mic = get_input(callback=callback_mic)
mic.start()
sleep(5)
mic.stop()
