======
Manual
======

Name
----

csvtranslator

Synopsis
--------

.. code-block:: bash

    csvtranslator [-task:print,translate,transcode,combine] [-lang_from:en,fr,...] [-lang_to:en,fr,...] [-keys_from:[,]] [-keys_to:[,]] [-source:] [-sources:[,]] [-destination:]

** Warning an empty destination will output in the source and replace it **

default options are:

.. code-block:: bash

    -lang_to:en
    -destination:source

Description
-----------

csvtranslator is a Python command line tool to manipulate csv files.

* Print
* Translate columns
* Combine csv files
* ...

Options
-------

-task:
======
[print,translate,transcode,combine]

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

See :doc:`warnings`

Examples
--------

.. code-block:: bash

    # Add a translated column to a csv file
    ./csvtranslator/csvtranslator.py -task:translate -source:~/Documents/titles_english.csv -destination:~/Documents/titles.csv -lang_from:en -lang_to:fr -keys_from:name_english -keys_to:name_french

    # Combine two csv files
    ./csvtranslator/csvtranslator.py -task:combine -sources:~/Documents/titles_english.csv,~/Documents/titles_french.csv -destination:~/Documents/titles.csv

More examples in :doc:`use_cases`

See Also
--------

`FFmpeg <https://ffmpeg.org/>`_

Author
------

Fabrice Quenneville
