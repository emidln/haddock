Haddock
=======

Haddock is a micro-framework for creating APIs. It is both the Python code to assemble the APIs and an API description format. It uses Klein and Twisted in the back end.

Haddock revolves around versions - it is designed so that you can write code for new versions of your API without disturbing old ones. You simply expand the scope of the unchanged methods, and copy a reference into your new version.

Why?
----

Because I liked the look of Praekelt's Aludel (https://github.com/praekelt/aludel) but it didn't kind of work how I thought it would. So, I wrote something similar, to play around!

How do I use it?
----------------

You need two things - the API description document, and the implementation.

You can find the example description document in `haddock/test` and the example Python in the root directory. Simply run `example.py` and navigate to http://localhost:8094/v1/weather?postcode=61000&unixTimestamp=1 for a demonstration.

More Detail
-----------

Check `docs/APIDescription.md` for more information on the API Description.