Haddock
=======

Haddock is a framework for easily creating APIs. It uses Python and Twisted, and supports both CPython 2.7 and PyPy.

Haddock revolves around versions - it is designed so that you can write code for new versions of your API without disturbing old ones. You simply expand the scope of the unchanged methods, and copy a reference into your new version.

Documentation can be found at `Read The Docs <http://haddock.readthedocs.org>`_.

Why?
----

Because I liked the look of `Praekelt's Aludel <https://github.com/praekelt/aludel>`_ but it didn't kind of work how I thought it would. So, I wrote something similar!

How do I use it?
----------------

You need two things - the API description document, and the implementation.

You can find the example description document and the example Python in the root directory. Simply run ``example.py`` and navigate to `this example endpoint <http://localhost:8094/v1/weather?postcode=61000&unixTimestamp=1>`_ for a demonstration.