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
import time
import collections

from lib.base.core import BaseDict, dump_personal_dict, load, load_offline_dict, load_personal_dict, offline_refer, personal_refer
from lib.speech.mfcc import mfcc
from lib.speech.dtw import dtw

# For android audio recording
from audiostream import get_input, get_output, get_input_sources, AudioSample
import time
import binascii

import kivy
from kivy.logger import Logger
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
from kivy.properties import ObjectProperty, StringProperty, DictProperty, NumericProperty
from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import FadeTransition
from kivy.core.window import Window
from kivy.metrics import dp

kivy.require("1.8.0")


######## Popup #########
class CollectPopup(Popup):
    """Popup when click collect button, which contain a button to sample the voice."""

    def __init__(self, target, **kargs):
        super(CollectPopup, self).__init__(**kargs)
        self.target = target
        self.wave = None

    def popupChoose(self):
        # Output stream initialize
        self.stream = get_output(channels=1, buffersize=1024, rate=8000)
        self.sample = AudioSample()
        self.stream.add_sample(self.sample)
        #Echo
        self.sample.stop()
        self.sample.play()
        self.sample.write(self.bin_data)
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
        # Calculate MFCC
        self.target.feature = mfcc(self.wave)
        personal_dict[self.target.word] = self.target
        mod_view_success = ModalView(auto_dismiss = True, size_hint=(.5, .1))
        mod_view_success.add_widget(Label(text="Successfully collect!"))
        mod_view_success.open()

######## Button #########
class SampleButton(Button):

    def __init__(self, **kargs):
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

        mic.stop()
        print "MIC ended..."

        # Remove the prepending Inpulse voice
        bin_data = ''.join(frames)[200:]
        wave = numpy.array([int(binascii.b2a_hex(i), 16) for i in bin_data])
        # Return both pure data and binary data string for speaker.
        return (wave, bin_data)


class EditButton(Button):
    edit_listview = ObjectProperty()
    flag = NumericProperty() #0: EDIT; 1: REMOVE
    app = ObjectProperty()

    def __init__(self, **kargs):
        super(EditButton, self).__init__(**kargs)

    def on_flag(self, *args):
        if self.flag is 0:
            self.text = "Edit"
            self.edit_listview.adapter.selection_mode = "none"
        else:
            self.text = "Remove"
            self.edit_listview.adapter.selection_mode = "multiple"

    def on_release(self, *args):
        if self.flag is 0:
            # EDIT -> REMOVE
            self.flag = 1
        else:
            # REMOVE -> EDIT
            self.remove_words(self.edit_listview.adapter.selection)
            self.flag = 0

    def remove_words(self, stuff):
        print "EditButton:: remove stuff: ", stuff
        for i in stuff:
            del self.app.root.personal_dict[i.text]
        # Update list view
        del self.edit_listview.adapter.data[:]
        self.edit_listview.adapter.data.extend(list(self.app.root.personal_dict.keys()))
        self.edit_listview._trigger_reset_populate()



class WordButton(ListItemButton):
    def on_release(self, *args):
        if (EdictApp.get_running_app().root.current is "manager") and \
           (EdictApp.get_running_app().root.current_screen.edit_button.flag is 1):
            pass
        else:
            EdictApp.get_running_app().root.show_word(self.text, flag = 0)

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

    def collect_desktop(self, word, meaning):
        personal_dict = EdictApp.get_running_app().root.personal_dict
        target = BaseDict(word)
        target.meaning = meaning
        personal_dict[word] = target



#######################
#       Offline Screen
#######################
class OfflineScreen(Screen):

    app = ObjectProperty()
    text_input = ObjectProperty()
    text = StringProperty()
    word_list = ObjectProperty()

    def __init__(self, **kargs):

        super(OfflineScreen, self).__init__(**kargs)
        self.offline_dict_keys = collections.defaultdict(list)

    def on_touch_move(self, touch):
        if touch.pos[1] < self.app.window.height - dp(self.text_input.parent.height):
            EdictApp.get_running_app().window.release_all_keyboards()

    def on_text(self, instance, text):

        print "Offline:", text
        if not self.offline_dict_keys:
            # Initiate the list of dict keys in the first time(classify to classes)
            for word in self.app.root.offline_idx_dict.keys():
                self.offline_dict_keys[word[0]].append(word)
        if text is "":
            candidates = []
        else:
            candidates = [w for w in self.offline_dict_keys[text[0]] if w.startswith(text)][:50]
        del self.word_list.adapter.data[:]
        self.word_list.adapter.data.extend(candidates)
        self.word_list._trigger_reset_populate()

    def refer(self, word, dikt):
        EdictApp.get_running_app().root.show_word(word, flag = 0)

#######################
#       Personal Screen
#######################
class PersonalScreen(Screen):

    app = ObjectProperty()
    text_input = ObjectProperty()
    text = StringProperty()
    word_list = ObjectProperty()

    def __init__(self, **kargs):

        super(PersonalScreen, self).__init__(**kargs)
        self.match = None
        self.event = threading.Event()
        self.personal_dict_keys = collections.defaultdict(list)

    def on_touch_move(self, touch):
        if touch.pos[1] < self.app.window.height - dp(self.text_input.parent.height):
            EdictApp.get_running_app().window.release_all_keyboards()

    def on_text(self, instance, text):

        print "Personal: ", text
        if not self.personal_dict_keys:
            print "Personal: Initiating self.personal_dict_keys..."
            # Initiate the list of dict keys in the first time(classify to classes)
            for word in self.app.root.personal_dict.keys():
                print "Personal: Adding word: %s to personal_dict_keys"%text
                self.personal_dict_keys[word[0]].append(word)

        if text is "":
            candidates = []
        else:
            candidates = [w for w in self.personal_dict_keys[text[0]] if w.startswith(text)][:50]
        del self.word_list.adapter.data[:]
        self.word_list.adapter.data.extend(candidates)
        self.word_list._trigger_reset_populate()

    def refer(self, word, dikt):
        EdictApp.get_running_app().root.show_word(word, flag = 1)

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
                self.event.clear()
                # Unschedule polling event.
                Clock.unschedule(self._poll_flag)
                self.app.root.show_word(self.match, flag = 1)


#######################
#       Manager Screen
#######################
class PersonalManagerScreen(Screen):
    edit_listview = ObjectProperty()
    edit_button = ObjectProperty()

    def args_converter(self, index, text):
        ret = {"text": text}
        return ret




#######################
#       Root          #
#######################
class EdictRoot(ScreenManager):
    personal_dict = DictProperty()
    offline_idx_dict = DictProperty()

    last_screen = ObjectProperty()

    def __init__(self, **kargs):
        super(EdictRoot, self).__init__(**kargs)
        # Get configurations
        #config = EdictApp.get_running_app().config
        #offline_path = config.get("Offline", "path")
        offline_path = EdictApp.get_running_app().landao_dict
        self.offline_idx_path = os.path.abspath(os.path.join(offline_path, [i for i in os.listdir(offline_path) if i.endswith(".idx")][0]))
        self.offline_dict_path = os.path.abspath(os.path.join(offline_path, [i for i in os.listdir(offline_path) if i.endswith(".dict")][0]))
        #self.personal_dict_path = config.get("Personal", "file")
        self.personal_dict_path = EdictApp.get_running_app().personal_dict

        # load offline index(dict)
        self.offline_idx_dict = load_offline_dict(self.offline_idx_path)

        # set last_keys
        self.last_keys = []

        # set load status
        self.loaded = 0

    def on_personal_dict(self, inst, p_dict):
        if not self.loaded:
            return
        # Dump to personal_dict_path
        dump_personal_dict(dict(self.personal_dict), self.personal_dict_path)
        print "dumping persona_dict..."

        # Update personal_dict_keys in PersonalScreen
        self.current_keys = self.personal_dict.keys()
        increment = len(self.current_keys) - len(self.last_keys)
        diff = set(self.current_keys) - set(self.last_keys) if set(self.current_keys) - set(self.last_keys) else set(self.last_keys) - set(self.current_keys)
        diff = list(diff)[0]
        if increment is 1:
            self.get_screen("personal").personal_dict_keys[diff[0]].append(diff)
            print "ROOT: add word: %s to personal_dict_keys"%diff
        elif increment is -1:
            self.get_screen("personal").personal_dict_keys[diff[0]].remove(diff)
            print "ROOT: rm word: %s from personal_dict_keys"%diff
        self.last_keys = self.current_keys

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
        if not self.personal_dict:
            # First time: load personal dict
            self.personal_dict = load_personal_dict(self.personal_dict_path)
            self.last_keys = self.personal_dict.keys()

            # set loaded
            self.loaded = 1

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
        del self.get_screen("manager").edit_listview.adapter.data[:]
        self.get_screen("manager").edit_listview.adapter.data.extend(list(self.personal_dict.keys()))
        self.get_screen("manager").edit_listview._trigger_reset_populate()
        # switch
        self.transition = FadeTransition()
        self.current = "manager"

    def show_word(self, word, flag):
        """flag: 0 - offline; 1 - personal"""
        # save last screen
        self.last_screen = self.current
        # get meaning
        if not flag:
            meaning = offline_refer(self.offline_dict_path, self.offline_idx_dict, word)
        else:
            meaning = personal_refer(self.personal_dict, word)
        # Action
        if meaning:
            # modify content
            self.get_screen("word").word.text = word
            self.get_screen("word").meaning.text = meaning
            # switch
            self.transition = FadeTransition()
            self.current = "word"
        else:
            modview = ModalView(auto_dismiss = True, size_hint=(.85, .1))
            modview.add_widget(Label(text = "Word %s not found!"%word))
            modview.open()


    def show_last_screen(self):
        if self.last_screen == "word":
            self.show_word(self.get_screen("word").word.text, self.get_screen("word").meaning.text)
        else:
            functions = [self.show_offline, self.show_personal, self.show_personal_manager]
            index = ["offline", "personal", "manager"].index(self.last_screen)
            functions[index]()

################################################
#        App                                   #
################################################
class EdictApp(App):

    def on_start(self):
        Logger.info("APP: I'm alive!")

    def build(self):
        self.icon = "icon.png"

        # Get window
        self.window = Window

        # Create the root widget
        self.root = EdictRoot(app = self)

    def build_config(self, config):
        # Font
        self.font = os.path.abspath(os.path.join(os.path.curdir, "fonts", "DroidSansFallback.ttf"))
        #config.setdefaults("Font", {"file": font})
        # Offline
        self.landao_dict = os.path.abspath(os.path.join(os.path.curdir, "dict_collections", "langdao-ec-gb"))
        #config.setdefaults("Offline", {"path": landao_dict})
        # Personal
        self.personal_dict = os.path.abspath(os.path.join(os.path.curdir, "dict_collections", "personal_dict", "personal_dict.pkl"))
        #config.setdefaults("Personal", {"file": personal_dict})

    #def build_settings(self, settings):
    #    settings.add_json_panel("Edict Settings", self.config, "settings.json")

if __name__ == "__main__":
    EdictApp().run()
