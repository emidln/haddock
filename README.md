Haddock
=======

Haddock is a micro-framework for creating APIs, as well as a JSON-based API description language. It uses Klein and Twisted in the back end.

Why?
----

Because I liked the look of Praekelt's Aludel (https://github.com/praekelt/aludel) but it didn't kind of work how I thought it would. So, I wrote something similar, to play around!

How do I use it?
----------------

You need two things - the API description document, and the implementation. You can find the description document in `examples` and the example python in the root directory. Simply run `example.py` and navigate to `http://localhost:8094/v2/weather?countryCode=US&postcode=61000&unixTimestamp=1` for a demonstration.

More Detail
-----------

Check `docs/APIDescription.md` for more information on the API Description.