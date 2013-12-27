==========================
An Introduction To Haddock
==========================

Haddock was made to help you create simple APIs that divide cleanly over versions, with minimal fuss - Haddock takes care of routing, assembly, parameter checking and (optionally) authentication for you. All you have to do is provide your business logic.

Installing
==========

To install, you simply need to run::
    
    pip install haddock

This'll install Haddock and all its dependencies.

A Very Simple Example
=====================

In this introduction, we will create a *Planet Information* API. We will create something that will allow us to query it, and will return some information about planets. So, first, let's define our API.

Simple API Definition
---------------------

Put the following in ``planets.json``::

    {
        "metadata": {
            "name": "planetinfo",
            "friendlyName": "Planet Information",
            "versions": [1]
        },
        "api": [
            {
                "name": "yearlength",
                "friendlyName": "Year Length of Planets",
                "endpoint": "yearlength",
                "getProcessors": [
                    {
                        "versions": [1],
                        "requiredParams": ["name"]
                    }
                ]
            }
        ]
    }

Now, we have made a ``metadata`` section that gives three things:

- The 'name' of our API.
- The 'friendly name' (human-readable) name of our API.
- A list of versions that our API has (right now, just 1).

We then define an ``api`` section, which is a list of our different APIs. We have defined only one here, and we have said that:

- It has a name of 'yearlength'.
- It has a human-readable name of 'Year Length of Planets'.
- It has an endpoint of 'yearlength'. Haddock structures APIs as ``/<VERSION>/<ENDPOINT>``, so this means that a v1 of it will be at ``/v1/yearlength``.

There is also then ``getProcessors`` - a list of *processors*. A processor in Haddock is the code that actually does the heavy lifting. This one here only has two things - a list of versions that this processor applies to (in this case, just ``1``), and a list of required parameters (just the one, ``name``).

Using this API description, we can figure out that our future API will be at ``/v1/yearlength`` and require a single parameter - the name of the planet.

Now, lets make the processor behind it.

Simple Python Implementation
----------------------------

Put the following in ``planets.py``::

    import json
    from haddock.api import API

    class PlanetAPI(object):
        class v1(object):
            def yearlength_GET(self, request, params):
                pass

    APIDescription = json.load(open("planets.json"))
    myAPI = API(PlanetAPI, APIDescription)
    myAPI.getApp().run("127.0.0.1", 8094)

This example can be this brief because Haddock takes care of nearly everything else.

So, let's break it down. 

1. First we import ``API`` from ``haddock.api`` - this is what takes care of creating your API from the config.
2. We then create a ``PlanetAPI`` class, and make a subclass called ``v1``. This corresponds to version 1 of your API.
3. We then create a method called ``yearlength_GET``. This is done in a form of ``<NAME>_<METHOD>``. It has three parameters - ``self`` (this is special, we'll get to it later), ``request`` (the Twisted.Web Request for the API call) and ``params`` (rather than have to parse them yourself, Haddock does this for you).

Currently, ``yearlength_GET`` does nothing, so lets fill in some basic functionality - for brevity, we'll only support Earth and Pluto.
::

    def yearlength_GET(self, request, params):
        planetName = params["name"].lower()
        if planetName == "earth":
            return {"seconds": 31536000}
        elif planetName == "pluto":
            return {"seconds": 7816176000}

As you can see, we access ``params``, which is a dict of all the things given to you in the API call. This is sorted out by Haddock, according to your API description - it makes sure that all required parameters are there, and throws an error if it is not.

We then return a ``dict`` with our result. You can do this - Haddock will JSONise it automatically for you.

Running
-------

Let's try and run it!

``python planets.py``

This should print something out like this::

    2013-12-27 11:46:21+0800 [-] Log opened.
    2013-12-27 11:46:21+0800 [-] Site starting on 8094
    2013-12-27 11:46:21+0800 [-] Starting factory <twisted.web.server.Site instance at 0x192d998>

This says that the Twisted.Web server behind Haddock has started up, and is on the port we asked it to.

Now, go to ``http://localhost:8094/v1/yearlength?name=earth`` in your web browser. You should get the following back::

    {"status": "success", "data": {"seconds": 31536000}}

Now try ``http://localhost:8094/v1/yearlength`` - that is, without specifying the name.
::

    {"status": "fail", "data": "Missing request parameters: 'name'"}

As you can see, it fails if we don't pass in what we want.

API Documentation
-----------------

Tired of having to document your APIs? Well, with Haddock, you can provide basic API documentation *automatically*. Simply go back to your ``planets.json`` and make your ``metadata`` look like this::

    "metadata": {
        "name": "planetinfo",
        "friendlyName": "Planet Information",
        "versions": [1],
        "apiInfo": true
    },

Then restart your ``planets.py`` and browse to ``http://localhost:8094/v1/apiInfo``. You will get a list of what APIs you have, and some request and response params. It is a bit lacking right now - you'll only have ``name`` in Request Arguments with no other documentation, but you'll find out how to add descriptions and types to this documentation in the more advanced articles.

Going Further
=============

Haddock has a lot more functionality - optional parameters, specifying specific return or request parameters, authentication, and even more to do with automatic API documentation. Browse through the other documentation articles to see how to use these features.