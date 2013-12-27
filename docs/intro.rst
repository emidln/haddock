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
1. g