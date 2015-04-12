#!/bin/env python
# -*- coding: utf-8 -*-

#########################################################################
# Author: Zhaoting Weng
# Created Time: Sun 07 Dec 2014 03:33:01 PM CST
# File Name: core.py
# Description:
#       This module provides following routines:
#       1. Load and dump dictionaries.
#       2. Refer word in both dictionaries.
#########################################################################

import pickle
import edict.lib.base.dparser as dparser
import os

###########################################################
#               Base Class                                #
###########################################################
class BaseDict():
    """Class: BaseDict. Provide base entries for single new word.
    Attribute:
        self.word: Vocabulary literal
        self.meaning: Meaning of the word
        self.feature: MFCC coefficient of the word"""
    def __init__(self, word):
        self.word = word
        self.meaning= ''
        self.feature = None

###########################
#     Get Configuration   #
###########################
#def get_conf(global_dict):
#    """Get configuration for this app, which determines where the offline dictionary locates"""
#
#    home = os.curdir                        # Default
#    if 'HOME' in os.environ:
#        home = os.environ['HOME']
#    elif os.name == 'posix':
#        home = os.path.expanduser("~/")
#    elif os.name == 'nt':
#        if 'HOMEPATH' in os.environ:
#            if 'HOMEDRIVE' in os.environ:
#                home = os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']
#            else:
#                home = os.environ['HOMEPATH']
#
#    edictrc = os.path.join(home, ".edictrc.py")
#    try:
#        f = open(edictrc)
#    except IOError:
#        pass
#    else:
#        f.close()
#        execfile(edictrc, global_dict)

###########################
#       dump              #
###########################
def dump_personal_dict(p_dict, personal_dict_path):
    """Dump data structure into personal dict residing in disk.
    :param p_dict: python dictionary type object representing the whole cotent of personal dictionary.
    :param personal_dict_path: path to the .pkl file, representing personal dictionary.
    :returns: None
    """
    with open(personal_dict_path, "wb") as f:
        pickle.dump(p_dict, f, 1)
    return None

###########################
#       load              #
###########################
def load(personal_dict_path, offline_idx_path, offline_dict_path):
    """Load both offline and personal dictionaries.
    :param personal_dict_path: path to the .pkl file representing personal dictionary.
    :param offline_idx_path: path to the offline dictionary .idx file.
    :param offline_dict_path: path to the offline dictionary .dict file.

    :returns: tuple containing two dictionary type objects, representing both dictionaries' content.
    """
    # ------------------------
    # Load personal dictionary
    # ------------------------
    personal_dict = load_personal_dict(personal_dict_path)
    # ------------------------
    # Load offline dictionary
    # -----------------------
    offline_dict = load_offline_dict(offline_idx_path, offline_dict_path)
    return (personal_dict, offline_dict)

def load_personal_dict(personal_dict_path):
    """Load personal dictionary.

    :param personal_dict_path: path to the .pkl file representing personal dictionary.
    :returns: python dictionary object representing personal dictionary's content if it exsists;
              Otherwise, create one and return empty dict.
    """
    print "- Loading personal dictionary: %s..." % personal_dict_path
    try:
        # Load exsisting personal dictionary.
        with open(personal_dict_path, "rb") as f:
            personal_dict = pickle.load(f)
            print "- Loading personal dictionary: %s completed!" % personal_dict_path
            return personal_dict
    except IOError:
        print "---- Personal dictionary is not found!\n---- Creating one..."
        f = open(personal_dict_path, 'wb')
        pickle.dump({}, f, 1)
        f.close()
        print "---- Personal dictionary creation completed!"
        return {}

def load_offline_dict(offline_idx_path, offline_dict_path):
    """Load offline dictionary.
    :param offline_idx_path: path to the offline dictionary .idx file.
    :param offline_dict_path: path to the offline dictionary .dict file.
    :returns: python dictionary object representing offline dictionary's content if it exsists, or return None.
    """
    offline_parsed_dict_path = offline_idx_path[:offline_idx_path.find(".")]+".pkl"
    print "- Loading offline dictionary: %s..." % offline_parsed_dict_path
    try:
        with open(offline_parsed_dict_path, "rb") as f:
            offline_dict = pickle.load(f)
            print "- Loading offline dictionary: %s completed!" % offline_parsed_dict_path
            return offline_dict
    except IOError:
        try:
            print "---- Offline dictionary is not parsed!\n---- Parsing...."
            offline_dict = dparser.dict_parser(offline_idx_path, offline_dict_path)
            f = open(offline_parsed_dict_path, 'wb')
            pickle.dump(offline_dict, f, 1)
            f.close()
            print "---- Offline dictionary parseing completed!"
            print "- Loading offline dictionary: %s completed!" % offline_parsed_dict_path
            return offline_dict
        except IOError:
            print "- Offline dictionary not found!"
            return None

###########################
#     Refer               #
###########################
def offline_refer(off_dict, word):
    """Refer word in offline dictionary.
    :param off_dict: python object representing offline dictionary.
    :param word: word to refere.
    :returns: Meaning of the word.
    """

    if word.strip() in off_dict.keys():
        return off_dict[word]
    else:
        return False

def personal_refer(p_dict, word):
    """ Refer word in personal dictionary.
    :param p_dict: python object representing personal dictionary.
    :param word: word to refer.
    :returns: Meaning of word.
    """
    if word.strip() in p_dict.keys():
        return p_dict[word].meaning
    else:
        return False


