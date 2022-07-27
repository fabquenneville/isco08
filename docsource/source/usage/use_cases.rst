=========
Use cases
=========

The main reasons to use csvtranslator would be the following:

* :ref:`translate` do this:
* :ref:`combine` do that:

.. _translate:

Add a translated column to a csv file
-------------------------------------

By running this command you can add a translated column to a csv file:

.. code-block:: bash

    ./csvtranslator/csvtranslator.py -task:translate -source:~/Documents/titles_english.csv -destination:~/Documents/titles.csv -lang_from:en -lang_to:fr -keys_from:name_english -keys_to:name_french

.. _combine:

Do that
-------

By running that command you can combine two csv files:

.. code-block:: bash

    ./csvtranslator/csvtranslator.py -task:combine -sources:~/Documents/titles_english.csv,~/Documents/titles_french.csv -destination:~/Documents/titles.csv

