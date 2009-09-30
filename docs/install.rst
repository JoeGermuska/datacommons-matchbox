************
Installation
************

The toolkit has a number of external dependencies which must be satisfied
before it can be used on a local machine.

These dependencies include:

* `mongoDB 1.0 <http://mongodb.org/>`_
* `pymongo <http://pypi.python.org/pypi/pymongo/>`_
* `Sphinx Search <http://sphinxsearch.com/>`_ and its sphinxapi python client

Installation of mongoDB
=======================

#. `Download mongoDB 1.0 for your OS <http://www.mongodb.org/display/DOCS/Downloads>`_
#. Extract mongoDB and ensure that the files are somewhere on your path 
   (ie. you can type mongo on the command line and it opens a mongo client)
#. Install pymongo.  There are several ways to do this:
    * ``pip install [-E virtualenv] pymongo``
    * ``easy_install pymongo``
    * Or `download from PyPI <http://pypi.python.org/pypi/pymongo/0.16>`_ and
      install manually.

Installation of Sphinx Search
=============================

#. `Download latest release <http://sphinxsearch.com/downloads.html>`_
    ex: ``wget http://sphinxsearch.com/downloads/sphinx-0.9.9-rc2.tar.gz``
#. Extract source tarball
    ex: ``tar xvf sphinx-0.9.9-rc2.tar.gz``
#. Build sphinx search with 64-bit id support and xmlpipe2 enabled [#xml]_
    ex: ``./configure --without-mysql --without-pgsql --enable-id64 && make``
#. Install sphinx
    ex: ``make install``
#. Copy ``api/sphinxapi.py`` to somewhere on your ``PYTHONPATH``
    This step varies by operating system/python install, but should look
    like:
    
    ``cp api/sphinxapi.py /usr/lib/python2.6/dist-packages/``

.. [#xml] Be sure that libexpat is installed on your system before running
    configure. If you're unsure check the output of ./configure for a line
    that looks like "checking for libexpat... found".

Installation of project
=======================

Create the following directories:

#. data/mongo
#. data/sphinx
#. log