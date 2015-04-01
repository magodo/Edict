#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################################################
# Author: Zhaoting Weng
# Created Time: Sun 25 Jan 2015 09:27:06 PM CST
# File Name: main.py
# Description:
#########################################################################

import os
import sys

import threading
import numpy

from lib.base.core import get_conf, BaseDict, dump_personal_dict, load, load_personal_dict, offline_refer, personal_refer
from lib.speech.mfcc import mfcc
from lib.speech.dtw import dtw

# For android audio recording
from audiostream import get_input, get_output, get_input_sources, AudioSample
import time
import binascii

import kivy
import kivy.resources
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
from kivy.properties import ObjectProperty, StringProperty, DictProperty
from kivy.graphics import Color, Rectangle

kivy.require("1.8.0")


#######################
# Configuration
#######################
OFFLINE_IDX_PATH = os.path.join("dict_collections", "langdao-ec-gb.idx")
OFFLINE_DICT_PATH = os.path.join("dict_collections", "langdao-ec-gb.dict")
__personal_dict___ = os.path.abspath(os.path.join(os.path.curdir, 'personal_dict.pkl'))
__font__ = os.path.join("fonts", "DroidSansFallback.ttf")

#######################
#   Widgets           #
#######################

#----------------------
# TextInput
#----------------------
class ReferTextInput(TextInput):

    show_label = ObjectProperty()
    coll_button = ObjectProperty()

    def offlinerefer(self, offline_dict, word):
        meaning = offline_refer(offline_dict, word.strip())
        if meaning:
            self.show_label.text = meaning
            # Only after a word has meaning, then user could choose to collect this word
            self.coll_button.disabled = False
        else:
            self.show_label.text = "No translation for word: %s" %word

    def personalrefer(self, personal_dict, word):
        meaning = personal_refer(personal_dict, word.strip())
        if meaning:
            self.show_label.text = meaning
        else:
            self.show_label.text = "No translation for word: %s" %word


#----------------------
# Label
#----------------------
class ChineseLabel(Label):
    def __init__(self, **kargs):
        # Show Chinese
        self.font_name = kivy.resources.resource_find(__font__)
        super(ChineseLabel, self).__init__(**kargs)

#----------------------
# Buttons
#----------------------
class CollButton(Button):

    def show_view(self, word, meaning, personal_dict):
        """Show ModalView depends on if obj is True(word to collect), or False(Non word)"""

        self.disabled = True
        word = word.strip()
        if word in personal_dict.keys():
            # Exist
            ExistCollView().open()
        else:
            # Not exist
            obj = BaseDict(word)
            obj.meaning = meaning
            CollView(target = obj).open()

class SampleButton(Button):

    def __init__(self, **kargs):
        # Data store
        self.data = None
        self.bin_data = None

        # Output stream initialize
        self.stream = get_output(channels=1, buffersize=1024, rate=8000)
        self.sample = AudioSample()
        self.stream.add_sample(self.sample)

        super(SampleButton, self).__init__(**kargs)

    def startRecord(self, channels=1, encoding=16, rate=8000):
        def mic_callback(buf):
            print "got data", len(buf)
            frames.append(buf)
        frames = []
        # Need to set buffersize
        mic = get_input(callback=mic_callback, channels=channels, rate=rate, encoding=encoding, buffersize=1024)
        mic.start()
        print "MIC started..."
        time.sleep(.5)
        mic.poll()
        time.sleep(.5)
        mic.poll()
        time.sleep(.5)
        mic.poll()
        time.sleep(.5)
        mic.poll()

        mic.stop()
        print "MIC ended..."

        # Remove the prepending Inpulse voice
        bin_data = ''.join(frames)[200:]
        data = [int(binascii.b2a_hex(i), 16) for i in bin_data]

        # Return both pure data and binary data string for speaker.
        self.data = numpy.array(data)
        self.bin_data = bin_data

    def popupChoose(self):
        #Echo
        self.sample.stop()
        self.sample.play()
        self.sample.write(self.bin_data)

        p = CollChooseView(wave = self.data, target = self.target, last_view = self.parent.parent)
        p.open()

    def refer(self, personal_dict):
        target_feature = mfcc(self.data)
        match = None
        score = numpy.inf
        words = personal_dict.keys()

        if len(words) == 0:
            return None
        for word in words:
            if personal_dict[word].feature is not None:
                tmp_score = dtw(personal_dict[word].feature, target_feature)
                print "%s: %f" %(word, tmp_score)
                if tmp_score < score:
                    score = tmp_score
                    match = word
        return match

class ListWordButton(Button):

    def show(self, target):
        WordView(target = target).open()

class DeleteButton(Button):

    def delete(self, word, personal_dict, personal_dict_path):
        del personal_dict[word]
        # Convert kivy ObservableDict to python dict so that could be dumped by Pickle
        dump_personal_dict(dict(personal_dict), personal_dict_path)
        v = SuccessDelView(word = word, last_view = self.parent.parent)
        v.open()



#----------------------
# ModalView
#----------------------
class ExistCollView(ModalView):
    pass

class SuccessCollView(ModalView):
    pass

class CollView(ModalView):

    def __init__(self, target, **kargs):
        self.target = target
        super(CollView, self).__init__(**kargs)

    def collect(self, personal_dict, personal_dict_path):
        personal_dict[self.target.word] = self.target
        # Convert kivy ObservableDict to python dict so that could be dumped by Pickle
        dump_personal_dict(dict(personal_dict), personal_dict_path)
        SuccessCollView().open()

class CollChooseView(ModalView):
    def __init__(self, last_view, target, wave, **kargs):
        self.last_view = last_view
        self.target = target
        self.wave = wave
        super(CollChooseView, self).__init__(**kargs)

    def collect(self, personal_dict, personal_dict_path):
        self.target.feature = mfcc(self.wave)
        personal_dict[self.target.word] = self.target
        # Convert kivy ObservableDict to python dict so that could be dumped by Pickle
        dump_personal_dict(dict(personal_dict), personal_dict_path)
        SuccessCollView().open()

class WordView(ModalView):

    def __init__(self, target, **kargs):
        self.target= target
        super(WordView, self).__init__(**kargs)

class SuccessDelView(ModalView):

    def __init__(self, word, last_view, **kargs):
        self.word = word
        self.last_view = last_view
        super(SuccessDelView, self).__init__(**kargs)

#----------------------
# Layout
#----------------------

class WordLayout(GridLayout):
    wordset = DictProperty(load_personal_dict(__personal_dict___))

    def __init__(self, **kargs):
        super(WordLayout, self).__init__(**kargs)
        for word in sorted(self.wordset.keys()):
            btn = ListWordButton(text = word)
            self.add_widget(btn)

    def update(self):
        self.clear_widgets()
        for word in sorted(self.wordset.keys()):
            btn = ListWordButton(text = word)
            self.add_widget(btn)


#----------------------
# Screens
#----------------------
class HomeScreen(Screen):
    pass

class OffLineScreen(Screen):
    pass

class PersonalScreen(Screen):
    pass

class PersonalManagerScreen(Screen):
    pass

#----------------------
# ScreenManager
#----------------------
class EdictScreenManager(ScreenManager):
    pass

########################
#        App           #
########################
class EdictApp(App):

    personal_dict = DictProperty()
    offline_dict = DictProperty()

    def __init__(self, **kargs):

        # Load Dicts
        self.personal_dict_path = __personal_dict___
        self.personal_dict, self.offline_dict = load(__personal_dict___, OFFLINE_IDX_PATH, OFFLINE_DICT_PATH)
        super(EdictApp, self).__init__(**kargs)

    def build(self):
        return EdictScreenManager()



if __name__ == "__main__":
    EdictApp().run()



