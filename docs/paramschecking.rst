==================
Parameter Checking
==================

Haddock contains support for checking parameters given to your API. It supports checking for required and optional params, as well as restricting the content of each to certain values.

Required & Optional Params
==========================

This will show you how to use the required and optional params.

API Documentation
-----------------

Using the ``planets.json`` example from before, let's add a new API - this time, for getting the distance from the sun.
::

    {
        "metadata": {
            "name": "planetinfo",
            "friendlyName": "Planet Information",
            "versions": [1],
            "apiInfo": true
        },
        "api": [
            {
                "name": "sundistance",
                "friendlyName": "Distance from the Sun for Planets",
                "endpoint": "sundistance",
                "getProcessors": [
                    {
                        "versions": [1],
                        "requiredParams": ["name"],
                        "optionalParams": ["useImperial"],
                        "returnParams": ["distance"],
                        "optionalReturnParams": ["unit"]
                    }
                ]
            },
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

So now we've added a ``sundistance`` API, with a single processor. It has the following restrictions:

- For the request, ``name`` **must** be provided and ``useImperial`` **may** be.
- For the response, ``distance`` **must** be provided, and ``unit`` **may** be.

Python Implementation
---------------------

So, lets add the code to do this into ``planets.py``::

    import json
    from haddock.api import API, DefaultServiceClass

    class PlanetServiceClass(DefaultServiceClass):
        def __init__(self):
            self.yearLength = {
                "earth": {"seconds": 31536000},
                "pluto": {"seconds": 7816176000}
            }
            self.sunDistance = {
                "earth": {"smoots": 87906922100, "miles": 92960000},
                "pluto": {"smoots": 3470664162652, "miles": 3670050000}
            }

    class PlanetAPI(object):
        class v1(object):
            def yearlength_GET(self, request, params):
                planetName = params["name"].lower()
                return self.yearLength.get(planetName)

            def sundistance_GET(self, request, params):
                planetName = params["name"].lower()
                sunDistance = self.sunDistance.get(planetName)
                if sunDistance and params.get("useImperial"):
                    return {"distance": sunDistance["miles"]}
                else:
                    return {"distance": sunDistance["smoots"], "unit": "smoots"}

    APIDescription = json.load(open("planets.json"))
    myAPI = API(PlanetAPI, APIDescription, serviceClass=PlanetServiceClass())
    myAPI.getApp().run("127.0.0.1", 8094)

We now have an implementation that will return the *distance* if ``useImperial`` is some truthy value, and *distance* and *unit* otherwise. The API will not force you to specify ``useImperial`` as an API consumer, nor ``unit`` as a developer. Please note that not being specified will make it not appear in the dict, so using ``params.get()`` is a must!