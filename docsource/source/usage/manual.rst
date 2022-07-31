======
Manual
======

Name
----

csvtools

Synopsis
--------

.. code-block:: bash

    csvtools [-task:combine,print,print_longest,translate,transcode] [-lang_from:en,fr,...] [-lang_to:en,fr,...] [-keys_from:[,]] [-keys_to:[,]] [-source:] [-sources:[,]] [-destination:] [-id:] [-translator:]

** Warning an empty destination will output in the source and replace it **

default options are:

.. code-block:: bash

    -lang_to:en
    -destination:source

Description
-----------

csvtools is a Python command line tool to manipulate csv files.

* Print
* Translate columns
* Combine csv files
* ...

Options
-------

-task:
======
[combine,print,print_longest,translate,transcode]

Transcode will output random encoding to utf-8

-lang_from:
===========
The language to translate from: en,fr,es,...

-lang_to:
=========
The language to translate to: en,fr,es,...

-keys_from:
===========
A csv list of the keys to translate from.

-keys_to:
=========
A csv list of the keys to translate to.

-source:
========
A filepath to a csv file.

-sources:
=========
A csv list of filepaths to csv files.

-destination:
=============
A filepath to output to.

-id:
====
The id to use for trasks like combining csv's.

-translator:
============
The translator to use: argos or azure

See :doc:`warnings`

Examples
--------

.. code-block:: bash

    # Add a translated column to a csv file
    ./csvtools/csvtools.py -task:translate -source:~/Documents/titles_english.csv -destination:~/Documents/titles.csv -lang_from:en -lang_to:fr -keys_from:name_english -keys_to:name_french

    # Combine two csv files
    ./csvtools/csvtools.py -task:combine -sources:~/Documents/titles_english.csv,~/Documents/titles_french.csv -destination:~/Documents/titles.csv

More examples in :doc:`use_cases`

See Also
--------

`FFmpeg <https://ffmpeg.org/>`_

Author
------

Fabrice Quenneville
