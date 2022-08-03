#!/usr/bin/env python3
'''
    These are various tools used by mediacurator
'''

import configparser
import os
import sys
import copy
import csv
import re
import chardet
import shutil
import json
import requests
import uuid
# from googletrans import Translator, constants
# from google_trans_new import google_translator
# from translate import Translator
# import goslate
import argostranslate.package
import argostranslate.translate


def load_arguments():
    '''Get/load command parameters

    Args:

    Returns:
        arguments: A dictionary of lists of the options passed by the user
    '''
    arguments = {
        "id": None,
        "task": None,
        "translator": None,
        "lang_from": None,
        "lang_to": None,
        "key": None,
        "keys_from": [],
        "keys_to": [],
        "source": None,
        "sources": [],
        "destination": None,
    }

    for arg in sys.argv:
        if "-id:" in arg:
            arguments["id"] = arg[4:]
        elif "-task:" in arg:
            arguments["task"] = arg[6:]
        elif "-translator:" in arg:
            arguments["translator"] = arg[12:]
        elif "-lang_from:" in arg:
            arguments["lang_from"] = arg[11:]
        elif "-lang_to:" in arg:
            arguments["lang_to"] = arg[9:]
        elif "-key:" in arg:
            arguments["key"] = arg[5:]
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


def get_parent(filepath, level=1):
    '''Return a parent filepath {level} above the {filepath}

    Args:
        filepath: The starting point filepath
        level   : How many levels above filepaths should we return

    Returns:
        string: The requested filepath
    '''
    if level < 1:
        return os.path.dirname(filepath)
    return get_parent(os.path.dirname(filepath), level - 1)


def find_in_parents(file):
    '''Find a particular file in the parent directories.

    Args:
        file: The filename we are looking for

    Returns:
        config: The parsed configuration
    '''
    if not os.path.exists(file):
        for x in range(3):
            tmpfile = os.path.join(get_parent(__file__, x), file)
            if os.path.exists(tmpfile):
                file = tmpfile
    if not os.path.exists(file):
        return False
    return os.path.abspath(file)


def load_config(file="config.ini"):
    '''Load the configurations from an ini file

    Args:
        file: The config filename

    Returns:
        config: The parsed configuration
    '''
    config = configparser.ConfigParser()
    if find_in_parents(file):
        file = find_in_parents(file)
    config.read(file)
    return config._sections


def init_argos(from_code, to_code):
    '''Initialise an Argo translate engine, install the required languages and
        return the prepared translator engine.

    Args:
        from_code   : The ISO 639 code for a language to tranlate from: en,fr,es,...
        to_code     : The ISO 639 code for a language to tranlate to: en,fr,es,...

    Returns:
        config: A preconfigured Argos translate.Language object
    '''
    available_packages = argostranslate.package.get_available_packages()
    available_package = list(
        filter(lambda x: x.from_code == from_code and x.to_code == to_code,
               available_packages))[0]
    download_path = available_package.download()
    argostranslate.package.install_from_path(download_path)
    # installed_languages = argostranslate.translate.get_installed_languages()
    # from_lang = list(
    #     filter(lambda x: x.code == from_code, installed_languages))[0]
    # to_lang = list(filter(lambda x: x.code == to_code, installed_languages))[0]
    from_lang = argostranslate.translate.get_language_from_code(from_code)
    to_lang = argostranslate.translate.get_language_from_code(to_code)
    return from_lang.get_translation(to_lang)


def diclist_to_csv(diclist, destination, encoding='utf-8'):
    '''Write a list of dictionaries to a csv file.

    Args:
        diclist     : A list of dictionaries
        destination : The filepath of the destination csv.
        encoding    : The encoding to write the csv file with, defautls to utf-8.

    Returns:
    '''
    try:
        keys = diclist[0].keys()
        with open(destination, 'w', newline="", encoding=encoding) as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(diclist)
    except UnicodeEncodeError:
        diclist_to_csv(diclist, destination)


def translate_diclist_argos(diclist, lang_from='en', lang_to='fr', keys={}):
    '''Translate a list of dictionaries using argos.

    Args:
        diclist     : A list of dictionaries
        lang_from   : The ISO 639 code for a language to tranlate from: en,fr,es,...
        lang_to     : The ISO 639 code for a language to tranlate to: en,fr,es,...
        keys        : A dictionary of the keys names to translate from/to {"colen":"colfr",...}

    Returns:
        list        : diclist with the added translated columns
    '''
    csv_translated = []
    translator = init_argos(lang_from, lang_to)
    for data in diclist:
        for k_from, k_to in keys.items():
            if k_from in data:
                data[k_to] = translator.translate(data[k_from])
        csv_translated.append(data)
    return csv_translated


def translate_diclist_azure(diclist, lang_from='en', lang_to='fr', keys={}):
    '''Translate a list of dictionaries using azure.

    Args:
        diclist     : A list of dictionaries
        lang_from   : The ISO 639 code for a language to tranlate from: en,fr,es,...
        lang_to     : The ISO 639 code for a language to tranlate to: en,fr,es,...
        keys        : A dictionary of the keys names to translate from/to {"colen":"colfr",...}

    Returns:
        list        : diclist with the added translated columns
    '''
    config = load_config()
    if 'azure' not in config:
        return False

    endpoint = config['azure']['endpoint']
    constructed_url = f"{endpoint}/translate?api-version=3.0&from={lang_from}&to={lang_to}"

    headers = {
        'Ocp-Apim-Subscription-Key': config['azure']['subscription'],
        'Ocp-Apim-Subscription-Region': config['azure']['region'],
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    csv_translated = []
    for data in diclist:
        for k_from, k_to in keys.items():
            if k_from in data:
                body = [{'text': data[k_from]}]
                request = requests.post(
                    constructed_url, headers=headers, json=body)
                response = request.json()
                data[k_to] = response[0]['translations'][0]['text']
        csv_translated.append(data)
    return csv_translated


def translate_csv(source=None,
                  destination=None,
                  lang_from=None,
                  lang_to="en",
                  keys={},
                  translator="argos"):
    '''Translate a list of dictionaries using {translator}.

    Args:
        source      : The filepath for the source csv file
        destination : The filepath for the destination csv file
        lang_from   : The ISO 639 code for a language to tranlate from: en,fr,es,...
        lang_to     : The ISO 639 code for a language to tranlate to: en,fr,es,...
        keys        : A dictionary of the keys names to translate from/to {"colen":"colfr",...}
        translator  : The engine to use for the translation, defaults to argos (argos, azure)

    Returns:
        bool        : Success of the operation
    '''
    arguments = load_arguments()

    if arguments['source']:
        source = arguments['source']
    if not source:
        return False

    if not destination:
        destination = source

    if arguments['lang_from']:
        lang_from = arguments['lang_from']
    if arguments['lang_to']:
        lang_from = arguments['lang_to']
    if not lang_from:
        return False  # TODO detect language

    if arguments["keys_from"] and arguments["keys_to"]:
        keys = {}
        if len(arguments["keys_from"]) == len(arguments["keys_to"]):
            for i in range(len(arguments["keys_from"])):
                keys[arguments["keys_from"][i]] = arguments["keys_to"][i]
    if not keys:
        return False

    if not os.path.isfile(source):
        return False

    encoding = get_encoding_type(source).lower()
    csv_raw = csv.DictReader(open(source, encoding=encoding))
    if translator == 'azure':
        csv_translated = translate_diclist_azure(csv_raw, lang_from, lang_to,
                                                 keys)
    else:
        csv_translated = translate_diclist_argos(csv_raw, lang_from, lang_to,
                                                 keys)

    diclist_to_csv(csv_translated, destination, encoding)
    return True


def combine_csvs_lfl(sources, destination):
    '''Combine two csv files line for line and returns a list of dictionaries.

    Args:
        sources     : A list of filepaths for the source csv files
        destination : The filepath for the destination csv file

    Returns:
        combined_csv    : A list of dictionaries consisting of the combined csv files
        encoding        : The original encoding for the last source csv file
    '''
    if not sources:
        return False
    if not destination:
        return False
    encoding = 'utf-8'
    combined_csv = []
    for source in sources:
        if os.path.isfile(source):
            encoding = get_encoding_type(source).lower()
            csv_items = list(csv.DictReader(open(source, encoding=encoding)))
            for i in range(len(csv_items)):
                if i >= len(combined_csv):
                    combined_csv.append(csv_items[i])
                else:
                    for k, v in csv_items[i].items():
                        combined_csv[i][k] = v
    return combined_csv, encoding


def combine_csvs_id(sources, destination, id):
    '''Combine two csv by common id and returns a list of dictionaries.

    Args:
        sources     : A list of filepaths for the source csv files
        destination : The filepath for the destination csv file
        id          : The keyname for the unique id column

    Returns:
        combined_csv    : A list of dictionaries consisting of the combined csv files
        encoding        : The original encoding for the last source csv file
    '''
    if not sources:
        return False
    if not destination:
        return False
    encoding = 'utf-8'
    combined_csv = {}
    counta = 0
    countb = 0
    for source in sources:
        if os.path.isfile(source):
            encoding = get_encoding_type(source).lower()
            csv_items = csv.DictReader(open(source, encoding=encoding))
            for csv_item in csv_items:
                if not id in csv_item:
                    break
                if not csv_item[id] in combined_csv:
                    counta += 1
                    combined_csv[csv_item[id]] = csv_item
                else:
                    countb += 1
                    combined_csv[csv_item[id]] |= csv_item
    return list(combined_csv.values()), encoding


def combine_csvs_commons(sources, destination):
    '''Combine two csv by common column without being unique and returns a list of dictionaries.

    Args:
        sources     : A list of filepaths for the source csv files
        destination : The filepath for the destination csv file
        common          : The keyname for the common column

    Returns:
        combined_csv    : A list of dictionaries consisting of the combined csv files
        encoding        : The original encoding for the last source csv file
    '''
    if not sources:
        return False
    if not destination:
        return False
    encoding = 'utf-8'
    diclist = []
    keys = ()
    counta = 0
    countb = 0
    for source in sources:
        if os.path.isfile(source):
            encoding = get_encoding_type(source).lower()
            csv_items = list(csv.DictReader(open(source, encoding=encoding)))
            if len(diclist) < 1:
                diclist = csv_items
            else:
                diclist = fuse_diclists(diclist, csv_items)
    return diclist, encoding

def fuse_diclists(diclist1, diclist2):
    if len(diclist1) < 1 or len(diclist2) < 1:
        return False
    all_keys, common_keys = get_diclists_keys([diclist1, diclist2])

    diclist = []
    for dic1 in diclist1:
        toremove = []
        resdic = {k:None for k in all_keys}|dic1
        for i in range(len(diclist2)):
            for ck in common_keys:
                if resdic[ck] and ck in diclist2[i] and resdic[ck] == diclist2[i][ck]:
                    toremove.append(i)
                    diclist.append(copy.deepcopy(resdic)|diclist2[i])
            
        for i in sorted(toremove, reverse=True):
            del diclist2[i]
    for dic2 in diclist2:
        diclist.append({k:None for k in all_keys}|dic2)
    
    return diclist

def get_diclists_keys(diclists):
    '''Combine two csv and returns a list of dictionaries.

    Args:
        diclists    : A list of lists of dictionaries

    Returns:
        all_keys, common_keys : The keys
    '''
    all_keys = set()
    common_keys = set()
    for diclist in diclists:
        if len(diclists) < 1:
            continue
        common_keys = all_keys.intersection(diclist[0].keys())
        all_keys |= set(diclist[0].keys())
    return all_keys, common_keys


def compare_columns(source=None, keys_from={}, keys_to={}):
    '''

    Args:

    Returns:
    '''
    return False



def combine_csvs(sources, destination, id=None):
    '''Combine two csv and returns a list of dictionaries.

    Args:
        sources     : A list of filepaths for the source csv files
        destination : The filepath for the destination csv file
        id          : The keyname for the common column if there is one

    Returns:
        bool    : The success of the operations
    '''
    if not sources:
        return False
    if not destination:
        return False

    encoding = 'utf-8'
    combined_csv = None
    if not id:
        diclists = []
        for source in sources:
            encoding = get_encoding_type(source).lower()
            diclists.append(list(csv.DictReader(open(source, encoding=encoding))))
        all_keys, common_keys = get_diclists_keys(diclists)
        if len(common_keys) > 0:
            combined_csv, encoding = combine_csvs_commons(sources, destination)
        else:
            combined_csv, encoding = combine_csvs_lfl(sources, destination)
    else:
        combined_csv, encoding = combine_csvs_id(sources, destination, id)

    if combined_csv:
        diclist_to_csv(combined_csv, destination, encoding)
        return True
    return False


def break_csv(source=None, destination=None, key=None):
    '''

    Args:
        source      : The source filepath
        destination : The destination filepath

    Returns:
    '''

    if not os.path.isfile(source):
        return False
    if not destination:
        destination = source[:-4]
    if not key:
        return False

    encoding = get_encoding_type(source).lower()
    csv_raw = csv.DictReader(open(source, encoding=encoding))
    if not csv_raw:
        return False
    diclists = {}
    for d in csv_raw:
        if not d[key] in diclists:
            diclists[d[key]] = []
        diclists[d[key]].append(d)

    for k, v in diclists.items():
        if not os.path.isdir(destination):
            os.makedirs(destination)
        diclist_to_csv(v, os.path.join(destination, f"{k}.csv"), encoding)


def print_csv(filepath):
    '''Print a csv file

    Args:
        filepath: the filepath of the csv

    Returns:
        False: Failed operation
    '''
    if not os.path.isfile(filepath):
        return False

    csv_raw = csv.DictReader(
        open(filepath, encoding=get_encoding_type(filepath).lower()))
    for row in csv_raw:
        print(row)


def extract_columns(source, destination, keys_from=None, keys_to=None):
    '''Exctract columns from source csv and export them to destination.

    Args:
        sources     : A list of filepaths for the source csv files
        destination : The filepath for the destination csv file
        keys_from   : A list of the keys names to translate from
        keys_to     : A list of the keys names to translate to

    Returns:
        bool        : The success of the operations
    '''
    if not os.path.isfile(source):
        return False
    if not len(keys_from) > 0 and not len(keys_to) > 0:
        return False
    if not len(keys_from) == len(keys_to):
        return False

    encoding = get_encoding_type(source).lower()
    csv_raw = csv.DictReader(open(source, encoding=encoding))
    if not csv_raw:
        return False

    diclist = []
    for d in csv_raw:
        nd = {}
        for i in range(len(keys_from)):
            nd[keys_to[i]] = d[keys_from[i]].strip()
        diclist.append(nd)

    diclist_to_csv(diclist, destination, encoding)


def print_longest(path):
    if os.path.isdir(path):
        for filename in os.listdir(path):
            if filename.endswith('.csv'):
                print_longest(os.path.join(path, filename))
    else:
        if not os.path.isfile(path):
            return False
        csv_raw = csv.DictReader(
            open(path, encoding=get_encoding_type(path).lower()))
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
        print(f"Longuest values in {path}:")
        print(f"{t1:{longest_key}} | {t2}")
        for k, v in longests.items():
            print(f"{k:{longest_key}} | {v}")
        print()


def get_encoding_type(filepath=None, bytearr=None):
    if filepath and os.path.exists(filepath):
        with open(filepath, 'rb') as file:
            return chardet.detect(file.read())['encoding']
    elif bytearr:
        chardet.detect(bytearr)['encoding']


def transcode(source, destination=None, destination_codec='utf-8'):
    '''

    Args:
        source      : The source filepath
        destination : The destination filepath

    Returns:
    '''
    if os.path.isdir(source):
        for filename in os.listdir(source):
            if filename.endswith('.csv'):
                transcode(os.path.join(source, filename), destination)
    else:
        if not destination:
            destination = source
        print(f"Transcoding to utf-8: {source}")
        document = open(
            source, mode='r',
            encoding=get_encoding_type(source).lower()).read()
        document = document.encode(encoding=destination_codec, errors='strict')
        document = document.decode(encoding=destination_codec, errors='strict')
        document = document.replace(u"\u00a0", " ")
        open(destination, mode='w', encoding=destination_codec).write(document)


def move_all_files(source, destination):
    '''

    Args:
        source      : The source filepath
        destination : The destination filepath

    Returns:
    '''
    for file_name in os.listdir(source):
        file_from = os.path.join(source, file_name)
        file_to = os.path.join(destination, file_name)
        if os.path.isfile(file_from):
            shutil.move(file_from, file_to)
            print('Moved:', file_name)


def test01(source=None, destination=None):
    '''

    Args:
        source      : The source filepath
        destination : The destination filepath

    Returns:
    '''
    print("Testing! Testing!")
