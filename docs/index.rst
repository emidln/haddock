Haddock Documentation
=====================

.. image:: https://travis-ci.org/hawkowl/haddock.png?branch=master
.. image:: https://coveralls.io/repos/hawkowl/haddock/badge.png?branch=master

Haddock is a framework for easily creating APIs. It uses Python and Twisted, and supports both CPython 2.7 and PyPy.

Haddock revolves around versions - it is designed so that you can write code for new versions of your API without disturbing old ones. You simply expand the scope of the unchanged methods, and copy a reference into your new version.

You can get the MIT-licensed code on `GitHub <https://github.com/hawkowl/haddock>`_, or download it from `PyPI <https://pypi.python.org/pypi/haddock>`_.

Going Fishing, or - An Introduction
-----------------------------------

A look at Haddock, starting from the ground up.

.. toctree::
   :maxdepth: 2

   intro
   serviceclasses
   paramschecking
   authentication

Specifications
--------------

Haddock has a lot more functionality - optional parameters, specifying specific return or request parameters, authentication, and even more to do with automatic API documentation. Browse through the other documentation articles to see how to use these features.

.. toctree::
   apidescription