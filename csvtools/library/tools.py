#!/usr/bin/env python3
'''
    These are various tools used by mediacurator
'''

import configparser
from gettext import translation
import os
import sys
import csv
import re
import chardet
import shutil
import json
# from googletrans import Translator, constants
# from google_trans_new import google_translator  
# from translate import Translator
# import goslate
import argostranslate.package, argostranslate.translate


def load_arguments():
    '''Get/load command parameters

    Args:

    Returns:
        arguments: A dictionary of lists of the options passed by the user
    '''
    arguments = {
        "task"          : None,
        "lang_from"     : None,
        "lang_to"       : None,
        "keys_from"     : [],
        "keys_to"       : [],
        "source"        : None,
        "sources"        : [],
        "destination"   : None,
    }

    for arg in sys.argv:
        if "-task:" in arg:
            arguments["task"] = arg[6:]
        elif "-lang_from:" in arg:
            arguments["lang_from"] = arg[11:]
        elif "-lang_to:" in arg:
            arguments["lang_to"] = arg[9:]
        elif "-keys_from:" in arg:
            arguments["keys_from"] += arg[11:].split(",")
        elif "-keys_to:" in arg:
            arguments["keys_to"] += arg[9:].split(",")
        elif "-source:" in arg:
            arguments["source"] = arg[8:]
        elif "-sources:" in arg:
            arguments["sources"] += arg[9:].split(",")
        elif "-destination:" in arg:
            arguments["destination"] = arg[13:]

    return arguments

def get_parent(filepath, level = 1):
    if level < 1:
        return os.path.dirname(filepath)
    return get_parent(os.path.dirname(filepath), level - 1)

def find_in_parents(file):
    if not os.path.exists(file):
        for x in range(3):
            tmpfile = os.path.join(get_parent(__file__, x), file)
            if os.path.exists(tmpfile):
                file = tmpfile
    if not os.path.exists(file): return False
    return os.path.abspath(file)

def load_config(file = "config.ini"):
    '''Get/load command parameters

    Args:

    Returns:
        arguments: A dictionary of lists of the options passed by the user
    '''
    config = configparser.ConfigParser()
    find_in_parents(file)
    config.read(file)
    return config._sections

def init_argos(from_code, to_code):
    available_packages = argostranslate.package.get_available_packages()
    available_package = list(
        filter(
            lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
        )
    )[0]
    download_path = available_package.download()
    argostranslate.package.install_from_path(download_path)
    installed_languages = argostranslate.translate.get_installed_languages()
    from_lang = list(filter(
        lambda x: x.code == from_code,
        installed_languages))[0]
    to_lang = list(filter(
        lambda x: x.code == to_code,
        installed_languages))[0]
    return from_lang.get_translation(to_lang)


def translate_csv(source = None, destination = None, lang_from = None, lang_to = "en", keys = {}):
    if not source       : return False
    if not destination  : destination = source
    if not lang_from    : return False # TODO detect language
    if not keys         : return False

    translator = init_argos(lang_from, lang_to)

    csv_raw = None
    if os.path.isfile(source):
        csv_raw = csv.DictReader(open(source, encoding='utf-8'))

    csv_translated = []
    for data in csv_raw:
        for k_from, k_to in keys.items():
            if k_from in data:
                data[k_to] = translator.translate(data[k_from])
        csv_translated.append(data)

    keys = csv_translated[0].keys()
    with open(os.path.join(destination), 'w', newline = "", encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(csv_translated)

def combine_csvs(sources, destination):
    if not sources      : return False
    if not destination  : return False

    combined_lines = []
    for source in sources:
        if os.path.isfile(source):
            # csv_raw = csv.DictReader(open(source, encoding='utf-8'))
            with open(source) as file:
                lines = file.readlines()
                lines = [line.strip() for line in lines]
                for i in range(len(lines)):
                    if i >= len(combined_lines):
                        combined_lines.append(lines[i])
                    elif len(combined_lines[i]) == 0:
                        combined_lines[i] = lines[i]
                    elif combined_lines[i][-1] == ',':
                        combined_lines[i] += lines[i]
                    else:
                        combined_lines[i] += ',' + lines[i]

    with open(os.path.join(destination), 'w', newline = "", encoding='utf-8') as output_file:
        for row in combined_lines:
            output_file.write(f"{row}\n")

def print_csv(source):
    '''Get/load command parameters

    Args:

    Returns:
        arguments: A dictionary of lists of the options passed by the user
    '''
    csv_raw = None
    if os.path.isfile(source):
        csv_raw = csv.DictReader(open(source, encoding='utf-8'))

    for row in csv_raw:
        print(row)

def print_longest(source):
    '''Get/load command parameters

    Args:

    Returns:
        arguments: A dictionary of lists of the options passed by the user
    '''
    if not os.path.isfile(source): return False

    csv_raw = csv.DictReader(open(source, encoding=get_encoding_type(source).lower()))

    longest_key = 0
    longests = {}
    for row in csv_raw:
        for k, v in row.items():
            klen = len(k)
            if klen > longest_key:
                longest_key = klen

            vlen = len(v)
            if k not in longests:
                longests[k] = vlen
            elif vlen > longests[k]:
                longests[k] = vlen

    longest_key += 5
    t1 = "Column"
    t2 = "Length"
    print(f"{t1:{longest_key}} | {t2}")
    for k, v in longests.items():
        print(f"{k:{longest_key}} | {v}")

def get_encoding_type(file):
    with open(file, 'rb') as f:
        return chardet.detect(f.read())['encoding']

def transcode(source, destination):
    '''Get/load command parameters

    Args:

    Returns:
        arguments: A dictionary of lists of the options passed by the user
    '''
    print(f"Transcoding to utf-8: {source}")
    document = open(os.path.join(source), mode='r', encoding=get_encoding_type(source).lower()).read()
    document = document.encode(encoding = 'utf-8', errors = 'strict').decode(encoding = 'utf-8', errors = 'strict')
    document = document.replace(u"\u00a0", " ")
    open(os.path.join(destination), mode='w', encoding='utf-8').write(document)

def move_all_files(source, destination):
    '''Get/load command parameters

    Args:

    Returns:
        arguments: A dictionary of lists of the options passed by the user
    '''
    for file_name in os.listdir(source):
        file_from = os.path.join(source, file_name)
        file_to = os.path.join(destination, file_name)
        if os.path.isfile(file_from):
            shutil.move(file_from, file_to)
            print('Moved:', file_name)

def test01(source = None, destination = None):
    '''Get/load command parameters

    Args:

    Returns:
        arguments: A dictionary of lists of the options passed by the user
    '''
    print("Testing! Testing!")
