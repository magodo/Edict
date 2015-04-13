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

# Configure sys.path to include edict package
sys.path.append(os.path.abspath(os.path.join(os.path.curdir, os.path.pardir)))

import threading
import numpy
import time

from edict.lib.base.core import BaseDict, dump_personal_dict, load, load_personal_dict, offline_refer, personal_refer
from edict.lib.speech.mfcc import mfcc
from edict.lib.speech.dtw import dtw
from edict.lib.speech.waveio import keep_record, echo

import kivy
from kivy.app import App
from kivy.clock import Clock
import kivy.resources
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.listview import ListItemButton
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.modalview import ModalView
from kivy.properties import ObjectProperty, StringProperty, DictProperty
from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import FadeTransition

kivy.require("1.8.0")


######## Popup #########
class CollectPopup(Popup):
    """Popup when click collect button, which contain a button to sample the voice."""

    def __init__(self, target, **kargs):
        super(CollectPopup, self).__init__(**kargs)
        self.target = target
        self.wave = None

    def popupChoose(self):
        echo(self.wave)
        p = ChoosePopup(wave = self.wave, target = self.target, last_popup = self)
        p.open()

class ChoosePopup(Popup):

    def __init__(self, wave, target, last_popup, **kargs):
        super(ChoosePopup, self).__init__(**kargs)
        self.wave = wave
        self.target = target
        self.last_popup = last_popup

    def deny(self):
        self.dismiss()

    def accept(self):
        self.dismiss()
        self.last_popup.dismiss()
        # Get personal dict (path)
        personal_dict = EdictApp.get_running_app().root.personal_dict
        personal_dict_path = EdictApp.get_running_app().root.personal_dict_path
        # Calculate MFCC
        self.target.feature = mfcc(self.wave)
        personal_dict[self.target.word] = self.target
        dump_personal_dict(personal_dict, personal_dict_path)
        mod_view_success = ModalView(auto_dismiss = True, size_hint=(.5, .1))
        mod_view_success.add_widget(Label(text="Successfully collect!"))
        mod_view_success.open()

######## Button #########
class SampleButton(Button):

    def __init__(self, **kargs):
        self.stop_dict = {"flag": False}
        self.is_stopped = False
        self.wave = None
        super(SampleButton, self).__init__(**kargs)

    def startRecord(self):
        def t_startRecord():
            print "recording..."
            self.wave = keep_record(self.stop_dict)
            self.is_stopped = True
        t = threading.Thread(target = t_startRecord)
        t.start()

    def stopRecord(self):
        print "stopping..."
        self.stop_dict['flag'] = True
        while not self.is_stopped:
            pass
        # Prepare for next record
        self.stop_dict['flag'] = False
        self.is_stopped = False
        # Return wave data
        return self.wave

class WordButton(ListItemButton):
    pass

#######################
#       Word Screen
#######################
class WordScreen(Screen):
    word = ObjectProperty()
    meaning = ObjectProperty()

    def collect(self, word, meaning):
        # Get personal dict (path)
        personal_dict = EdictApp.get_running_app().root.personal_dict
        if word in personal_dict.keys():
            mod_view_exists = ModalView(auto_dismiss = True, size_hint=(.5, .1))
            mod_view_exists.add_widget(Label(text="Word already exists!"))
            mod_view_exists.open()
        else:
            target = BaseDict(word)
            target.meaning = meaning
            # Pop up voice button to record
            CollectPopup(target).open()


#######################
#       Offline Screen
#######################
class OfflineScreen(Screen):
    text_input = ObjectProperty()

    def refer(self, word, dikt):
        meaning = offline_refer(dikt, word)
        if meaning:
            EdictApp.get_running_app().root.show_word(word, meaning)
        else:
            modview = ModalView(auto_dismiss = True, size_hint=(.5, .1))
            modview.add_widget(Label(text = "Word %s not found!"%word))
            modview.open()

#######################
#       Personal Screen
#######################
class PersonalScreen(Screen):
    app = ObjectProperty()
    text_input = ObjectProperty()

    def __init__(self, **kargs):
        super(PersonalScreen, self).__init__(**kargs)
        self.match = None
        self.event = threading.Event()

    def refer(self, word, dikt):
        meaning = personal_refer(dikt, word)
        if meaning:
            EdictApp.get_running_app().root.show_word(word, meaning)
        else:
            modview = ModalView(auto_dismiss = True, size_hint=(.5, .1))
            modview.add_widget(Label(text = "Word %s not found!"%word))
            modview.open()

    def voice_refer(self):

        personal_dict = self.app.root.personal_dict
        personal_dict_is_empty = False if len(personal_dict.keys()) else True
        # Run as thread
        def _voice_refer():
            """Store the matched word to attr::self.match"""
            print "PID of '_voice_refer': ", threading.current_thread()
            words = personal_dict.keys()
            target_feature = mfcc(self.wave)
            match = None
            score = numpy.inf
            # For loop will block everything in app.
            # - it runs in the same thread as kivy's eventloop, so kivy can't do anything at all until it's finished.
            for word in words:
                progress.value += 1
                if personal_dict[word].feature is not None:
                    tmp_score = dtw(personal_dict[word].feature, target_feature)
                    print "%s: %f" %(word, tmp_score)
                    if tmp_score < score:
                        score = tmp_score
                        match = word
            self.match = match
            modview.dismiss()
            self.event.set()

        if personal_dict_is_empty:
            modview = ModalView(auto_dismiss = True, size_hint=(.85, .1))
            modview.add_widget(Label(text = "No word in personal dictionary!"))
            modview.open()
            return
        else:
            modview = ModalView(auto_dismiss = False, size_hint = (.85, .1))
            progress = ProgressBar(value = 0, max = len(personal_dict.keys()), size_hint = (.8, .8))
            modview.add_widget(progress)
            # Create thread to do the matching job
            t = threading.Thread(target = _voice_refer)
            modview.open()
            t.start()
            # Main thread poll the match flag, do other things in meanwhile
            Clock.schedule_interval(self._poll_flag, 0.1)

    def _poll_flag(self, *args):
        if self.event.isSet():
            if self.match:
                self.app.root.show_word(self.match, self.app.root.personal_dict[self.match].meaning)
                self.event.clear()
                # Unschedule polling event.
                Clock.unschedule(self._poll_flag)


#######################
#       Manager Screen
#######################
class PersonalManagerScreen(Screen):
    word_list = ObjectProperty()

#######################
#       Root          #
#######################
class EdictRoot(ScreenManager):
    personal_dict_path = StringProperty()
    personal_dict = ObjectProperty()
    offline_dict = ObjectProperty()

    last_screen = ObjectProperty()

    def __init__(self, **kargs):
        super(EdictRoot, self).__init__(**kargs)
        # Get configurations
        config = EdictApp.get_running_app().config
        offline_path = config.get("Offline", "Path")
        offline_idx_path = os.path.abspath(os.path.join(offline_path, [i for i in os.listdir(offline_path) if i.endswith(".idx")][0]))
        offline_dict_path = os.path.abspath(os.path.join(offline_path, [i for i in os.listdir(offline_path) if i.endswith(".dict")][0]))
        personal_dict_path = config.get("Personal", "Path")
        # Load
        self.personal_dict_path = personal_dict_path
        self.personal_dict, self.offline_dict = load(personal_dict_path, offline_idx_path, offline_dict_path)

    def show_offline(self):
        # save last screen
        self.last_screen = self.current
        # set focus
        self.get_screen("personal").text_input.focus = False
        self.get_screen("offline").text_input.focus = True
        # switch
        self.transition = FadeTransition()
        self.current = "offline"

    def show_personal(self):
        # save last screen
        self.last_screen = self.current
        # set focus
        self.get_screen("offline").text_input.focus = False
        self.get_screen("personal").text_input.focus = True
        # switch
        self.transition = FadeTransition()
        self.current = "personal"

    def show_personal_manager(self):
        # save last screen
        self.last_screen = self.current
        # Set list view
        del self.get_screen("manager").word_list.adapter.data[:]
        self.get_screen("manager").word_list.adapter.data.extend(list(EdictApp.get_running_app().root.personal_dict.keys()))
        self.get_screen("manager").word_list._trigger_reset_populate()
        # switch
        self.transition = FadeTransition()
        self.current = "manager"

    def show_word(self, word, meaning):
        # save last screen
        self.last_screen = self.current
        # modify content
        self.get_screen("word").word.text = word
        self.get_screen("word").meaning.text = meaning
        # switch
        self.transition = FadeTransition()
        self.current = "word"

    def show_last_screen(self):
        self.transition = FadeTransition()
        self.current = self.last_screen

################################################
#        App                                   #
################################################
class EdictApp(App):

    def build(self):
        self.icon = "icon.npg"
        # Create the root widget
        self.edict = EdictRoot(app = self)
        self.root = self.edict

    def build_config(self, config):
        # Font
        font = os.path.abspath(os.path.join(os.path.curdir, "fonts", "DroidSansFallback.ttf"))
        config.setdefaults("Font", {"Path": font})
        # Offline
        landao_dict = os.path.abspath(os.path.join(os.path.curdir, "dict_collections", "langdao-ec-gb"))
        config.setdefaults("Offline", {"Path": landao_dict})
        # Personal
        personal_dict = os.path.abspath(os.path.join(os.path.curdir, "personal_dict.pkl"))
        config.setdefaults("Personal", {"Path": personal_dict})

    def build_settings(self, settings):
        settings.add_json_panel("Edict Settings", self.config, "settings.json")

if __name__ == "__main__":
    EdictApp().run()
