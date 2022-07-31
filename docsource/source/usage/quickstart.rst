==========
Quickstart
==========

.. code-block:: bash

    csvtools [-task:combine,print,print_longest,translate,transcode] [-lang_from:en,fr,...] [-lang_to:en,fr,...] [-keys_from:[,]] [-keys_to:[,]] [-source:] [-sources:[,]] [-destination:] [-id:] [-translator:]

** Warning an empty destination will output in the source and replace it **

default options are:

.. code-block:: bash

    -lang_to:en
    -destination:source

Examples:

.. code-block:: bash

    # Add a translated column to a csv file
    ./csvtools/csvtools.py -task:translate -source:~/Documents/titles_english.csv -destination:~/Documents/titles.csv -lang_from:en -lang_to:fr -keys_from:name_english -keys_to:name_french

    # Combine two csv files
    ./csvtools/csvtools.py -task:combine -sources:~/Documents/titles_english.csv,~/Documents/titles_french.csv -destination:~/Documents/titles.csv

More examples in :doc:`use_cases`