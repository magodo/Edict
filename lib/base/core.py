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
import dparser
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
def load(personal_dict_path, offline_idx_path):
    """Load both offline idx and personal dictionaries.
    :param personal_dict_path: path to the .pkl file representing personal dictionary.
    :param offline_idx_path: path to the offline dictionary .idx file.

    :returns: tuple containing personal_dict and offline index dictionary.
    """
    # ------------------------
    # Load personal dictionary
    # ------------------------
    personal_dict = load_personal_dict(personal_dict_path)
    # ------------------------
    # Load offline dictionary
    # -----------------------
    idx_dict = load_offline_dict(offline_idx_path)
    return (personal_dict, idx_dict)

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

def load_offline_dict(offline_idx_path):
    """Load offline index dictionary.
    :param offline_idx_path: path to the offline dictionary .idx file.
    :returns: python dictionary object with 'word-index' pair.
    """
    print "- Loading offline index dictionary: %s..." % offline_idx_path
    try:
        idx_dict = dparser.create_idx_dict(offline_idx_path)
        print "- Loading offline index dictionary: %s completed!" % offline_idx_path
        return idx_dict
    except IOError:
        print "- Offline index dictionary not found!"
        return None

###########################
#     Refer               #
###########################
def offline_refer(dict_file, idx_dict, word):
    """Refer word in offline dictionary."""

    word = word.strip()
    if word in idx_dict.keys():
        return dparser.refer_word(dict_file, idx_dict, word)
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


if __name__ == "__main__":

    OFFLINE_IDX_PATH = "../../dict_collections/langdao-ec-gb/langdao-ec-gb.idx"
    OFFLINE_DICT_PATH = "../../dict_collections/langdao-ec-gb/langdao-ec-gb.dict"
    PERSONAL_DICT_PATH = "../../dict_collections/personal_dict/personal_dict.pkl"
    p_dict, idx_dict = load(PERSONAL_DICT_PATH, OFFLINE_IDX_PATH)
    print offline_refer(OFFLINE_DICT_PATH, idx_dict, "python")
