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

from edict.lib.base.core import BaseDict, dump_personal_dict, load, load_personal_dict, offline_refer, personal_refer
from edict.lib.speech.mfcc import mfcc
from edict.lib.speech.dtw import dtw
from edict.lib.speech.waveio import keep_record, echo

import kivy
import kivy.resources
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.listview import ListItemButton
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

debug = None

########################
##   Widgets           #
########################
#
##----------------------
## Buttons
##----------------------
#
#class SampleButton(Button):
#
#    def __init__(self, **kargs):
#        self.stop_dict = {"flag": False}
#        self.is_stopped = False
#        self.data = None
#        super(SampleButton, self).__init__(**kargs)
#
#    def startRecord(self):
#        def t_startRecord():
#            print "recording..."
#            self.data = keep_record(self.stop_dict)
#            self.is_stopped = True
#        t = threading.Thread(target = t_startRecord)
#        t.start()
#
#    def stopRecord(self):
#        print "stopping..."
#        self.stop_dict['flag'] = True
#        while not self.is_stopped:
#            pass
#        # Prepare for next record
#        self.stop_dict['flag'] = False
#        self.is_stopped = False
#
#    def popupChoose(self):
#        echo(self.data)
#        p = CollChooseView(wave = self.data, target = self.target, last_view = self.parent.parent)
#        p.open()
#
#    def refer(self, personal_dict):
#        target_feature = mfcc(self.data)
#        match = None
#        score = numpy.inf
#        words = personal_dict.keys()
#
#        if len(words) == 0:
#            return None
#        for word in words:
#            if personal_dict[word].feature is not None:
#                tmp_score = dtw(personal_dict[word].feature, target_feature)
#                print "%s: %f" %(word, tmp_score)
#                if tmp_score < score:
#                    score = tmp_score
#                    match = word
#        return match
#
#class WordButton(Button):
#
#    def show(self, target):
#        WordView(target = target).open()
#
#class DeleteButton(Button):
#
#    def delete(self, word, personal_dict, personal_dict_path):
#        del personal_dict[word]
#        # Convert kivy ObservableDict to python dict so that could be dumped by Pickle
#        dump_personal_dict(dict(personal_dict), personal_dict_path)
#        v = SuccessDelView(word = word, last_view = self.parent.parent)
#        v.open()
#
##----------------------
## ModalView
##----------------------
#class ExistCollView(ModalView):
#    pass
#
#class SuccessCollView(ModalView):
#    pass
#
#class CollView(ModalView):
#
#    def __init__(self, target, **kargs):
#        self.target = target
#        super(CollView, self).__init__(**kargs)
#
#    def collect(self, personal_dict, personal_dict_path):
#        personal_dict[self.target.word] = self.target
#        # Convert kivy ObservableDict to python dict so that could be dumped by Pickle
#        dump_personal_dict(dict(personal_dict), personal_dict_path)
#        SuccessCollView().open()
#
#class CollChooseView(ModalView):
#    def __init__(self, last_view, target, wave, **kargs):
#        self.last_view = last_view
#        self.target = target
#        self.wave = wave
#        super(CollChooseView, self).__init__(**kargs)
#
#    def collect(self, personal_dict, personal_dict_path):
#        self.target.feature = mfcc(self.wave)
#        personal_dict[self.target.word] = self.target
#        # Convert kivy ObservableDict to python dict so that could be dumped by Pickle
#        dump_personal_dict(dict(personal_dict), personal_dict_path)
#        SuccessCollView().open()
#
#class WordView(ModalView):
#
#    def __init__(self, target, **kargs):
#        self.target= target
#        super(WordView, self).__init__(**kargs)
#
#class SuccessDelView(ModalView):
#
#    def __init__(self, word, last_view, **kargs):
#        self.word = word
#        self.last_view = last_view
#        super(SuccessDelView, self).__init__(**kargs)
#
##----------------------
## Layout
##----------------------
#
#class WordLayout(GridLayout):
#    wordset = DictProperty(load_personal_dict(__personal_dict___))
#
#    def __init__(self, **kargs):
#        super(WordLayout, self).__init__(**kargs)
#        for word in sorted(self.wordset.keys()):
#            btn = WordButton(text = word)
#            self.add_widget(btn)
#
#    def update(self):
#        self.clear_widgets()
#        for word in sorted(self.wordset.keys()):
#            btn = WordButton(text = word)
#            self.add_widget(btn)
#
##----------------------
## Screens
##----------------------
#class HomeScreen(Screen):
#    pass
#
#class OffLineScreen(Screen):
#    """Offline dictionary screen."""
#
#    def offlinerefer(self, offline_dict, word):
#        """Refer a word in offline_dict by keyboard input"""
#        meaning = offline_refer(offline_dict, word.strip())
#        if meaning:
#            self.coll_button.disabled = False
#            self.show_label.text = meaning
#        else:
#            self.show_label.text = "Word: %s not found" % self.textinput.text
#        return
#
#    def show_view(self, personal_dict):
#        """Show ModalView depends on if obj is True(word to collect), or False(Non word)"""
#        word = self.textinput.text.strip()
#        if word in personal_dict.keys():
#            # Exist
#            ExistCollView().open()
#        else:
#            # Not exist
#            obj = BaseDict(word)
#            obj.meaning = self.show_label.text
#            CollView(target = obj).open()
#
#
#class PersonalScreen(Screen):
#    """Personal dictionary screen."""
#
#    def personalrefer(self, personal_dict, word):
#        """Refer a word in personal_dict by keyboard input"""
#        meaning = personal_refer(personal_dict, word.strip())
#        if meaning:
#            self.show_label.text = meaning
#        else:
#            self.show_label.text = "Word: %s not found" % self.textinput.text
#        return
#
#    def sample_button_press(self):
#        """Record voice when pressed down"""
#        self.sample_button.startRecord()
#
#    def sample_button_release(self, personal_dict):
#        """Finish recording when release, and do the match"""
#        self.sample_button.stopRecord()
#        match = self.sample_button.refer(personal_dict)
#        if match:
#            self.show_label.text = personal_dict[match].meaning
#        else:
#            self.show_label.text = "No voiced word in Personal dictionary!"
#

######## Button #########
class WordButton(ListItemButton):
    pass


#######################
#       Word Screen
#######################
class WordScreen(Screen):
    word = ObjectProperty()
    meaning = ObjectProperty()

    def collect(self, word, meaning):
        personal_dict = EdictApp.get_running_app().root.personal_dict
        personal_dict_path = EdictApp.get_running_app().root.personal_dict_path
        if word in personal_dict.keys():
            mod_view_exists = ModalView(auto_dismiss = True, size_hint=(.5, .1))
            mod_view_exists.add_widget(Label(text="Word already exists!"))
            mod_view_exists.open()
        else:
            # Collect to personal dict
            target = BaseDict(word)
            target.meaning = meaning
            personal_dict[word] = target
            dump_personal_dict(personal_dict, personal_dict_path)
            mod_view_success = ModalView(auto_dismiss = True, size_hint=(.5, .1))
            mod_view_success.add_widget(Label(text="Successfully collect!"))
            mod_view_success.open()

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
    text_input = ObjectProperty()

    def refer(self, word, dikt):
        meaning = personal_refer(dikt, word)
        if meaning:
            EdictApp.get_running_app().root.show_word(word, meaning)
        else:
            modview = ModalView(auto_dismiss = True, size_hint=(.5, .1))
            modview.add_widget(Label(text = "Word %s not found!"%word))
            modview.open()

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
            # offline
        offline_path = config.get("Offline", "Path")
        offline_idx_path = os.path.abspath(os.path.join(offline_path, [i for i in os.listdir(offline_path) if i.endswith(".idx")][0]))
        offline_dict_path = os.path.abspath(os.path.join(offline_path, [i for i in os.listdir(offline_path) if i.endswith(".dict")][0]))
            # personal
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
