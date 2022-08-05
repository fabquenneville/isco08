=========
Use cases
=========

The main reasons to use isco08 would be the following:

* :ref:`translate`:
* :ref:`combine`:
* :ref:`printlongest`:

.. _translate:

Add a translated column to a csv file
-------------------------------------

By running this command you can add a translated column to a csv file:

.. code-block:: bash

    ./isco08/isco08.py -task:translate -source:~/Documents/titles_english.csv -destination:~/Documents/titles.csv -lang_from:en -lang_to:fr -keys_from:name_english -keys_to:name_french

.. _printlongest:

Print the lengths on the longuest values per column
---------------------------------------------------

By running this command you can add a translated column to a csv file:

.. code-block:: bash

    ./isco08/isco08.py -task:translate -source:~/Documents/titles_english.csv -destination:~/Documents/titles.csv -lang_from:en -lang_to:fr -keys_from:name_english -keys_to:name_french
    ./isco08/isco08.py -task:print_longest -source:'/mnt/workbench/data/canada_provinces.csv'
.. _combine:

Combine many csv files line for line
------------------------------------

By running that command you can combine two csv files:

.. code-block:: bash

    # Combining line by line
    ./isco08/isco08.py -task:combine -sources:~/Documents/titles_english.csv,~/Documents/titles_french.csv -destination:~/Documents/titles.csv
    # Combining by common id
    ./isco08/isco08.py -task:combine -id:columnname -sources:~/Documents/titles_english.csv,~/Documents/titles_french.csv -destination:~/Documents/titles.csv

