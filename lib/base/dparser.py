#!/usr/bin/env python
# This file include routine to parse English-Chinese star-dict format dictionary.
# Author: Zhaoting Weng 2014

def dict_parser(idx_file, dict_file):
    """Parse stardict formatted dictionary
    :param idx_file: star-dict .idx file.
    :param dict_file: star-dict .dict file.

    :returns: a dictionary type object representing the word-meaning pairs in the dictionary.
    """
    import binascii

    with open(idx_file, 'rb') as f:
        index_raw = f.read()
    with open(dict_file, 'rb') as f:
        dict_raw = f.read()

    end_point = 0
    offline_dict = {}                               # Store the off line dictionary as return variable

    while end_point < len(index_raw):
        tmp = end_point
        end_point = index_raw.index('\0', end_point)
        word = index_raw[tmp:end_point]
        tmp = end_point + 1

        bias = index_raw[tmp:tmp+4]
        bias = int(binascii.b2a_hex(bias), 16)

        length = index_raw[tmp+4:tmp+8]
        length = int(binascii.b2a_hex(length), 16)

        offline_dict[word] = dict_raw[bias:(bias+length)].decode('utf-8')
        end_point += 9

    return offline_dict

if __name__ == '__main__':
    #Test
    offline_dict = dict_parser('../../dict_collections/langdao-ec-gb.idx', '../../dict_collections/langdao-ec-gb.dict')
    for (key, value) in offline_dict.items()[:100]:
        print "%s:\n%s" % (key, value)



