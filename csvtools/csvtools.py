#!/usr/bin/env python3

# Normal import
try:
    from csvtools.library.tools import load_arguments, load_config, print_csv, print_longest, translate_csv, combine_csvs, transcode, test01
# Allow local import for development purposes
except ModuleNotFoundError:
    from library.tools import load_arguments, load_config, print_csv, print_longest, translate_csv, combine_csvs, transcode, test01

def main():
    arguments = load_arguments()
    source = arguments['source']
    sources = arguments['sources']
    destination = arguments['destination']
    if arguments['task'] == "print":
        print_csv(source)
    elif arguments['task'] == "translate":
        lang_from = arguments['lang_from']
        lang_to = arguments['lang_to']
        keys = {}
        if len(arguments["keys_from"]) == len(arguments["keys_to"]):
            for i in range(len(arguments["keys_from"])):
                keys[arguments["keys_from"][i]] = arguments["keys_to"][i]
        translate_csv(source, destination, lang_from, lang_to, keys)
    elif arguments['task'] == "transcode":
        transcode(source, destination)
    elif arguments['task'] == "combine":
        combine_csvs(sources, destination)
    elif arguments['task'] == "print_longest" and source:
        print_longest(source)
    elif arguments['task'] == "test":
        test01(source, destination)

if __name__ == '__main__':
    main()
