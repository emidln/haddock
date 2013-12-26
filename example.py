#!/usr/bin/python

# Import API (which assembles the API) and the DefaultServiceClass that you can
# use as the base for your service class.
from haddock.api import API, DefaultServiceClass
import json

class myServiceClass(DefaultServiceClass):
    def __init__(self):
        # Store things in your service class that you want to access in your
        # API's methods.
        self.weather = {"temperature": 30, "windSpeed": 20, "isRaining": False}

    def doSomething(self):
        # An example function, called from the inside of the API example.
        return self.weather


class APIExample(object):
    # An API is made up of versions - each in a different class, to keep things
    # a little bit neat.
    class v1(object):
        def weather_GET(self, request, params):
            # Call a method on your service class.
            # Note that `self` is a reference to your service class, and not
            # `APIExample.v1` here! Haddock changes this for you.
            return self.doSomething()

    class v2(object):
        def __init__(self, outer):
            # `outer` is actually the a reference to the master `APIExample`.
            # You don't need to have `__init__` defined, but you can do stuff
            # here if you wanted to!
            # For example to migrate a processor from v1 to v2, you could do:
            # self.someapi_GET = outer.v1.someapi_GET
            pass

        def weather_GET(self, request, params):
            # Just return an object - Haddock will check it according to your
            # API definition and JSONise it. You'll notice that this is
            # different to what v1 returns - different processors can require
            # different things. Check APIExample.json to see what makes
            # Weather v1 and Weather v2 different.
            return {"temperature": 30, "windSpeed": 20, "isRaining": "YES"}


myAPI = API(
    APIExample, # Pass in your API class.
    json.load(open("APIExample.json")), # Load your API definition and give it
                                        # to Haddock to build your API with.
    serviceClass=myServiceClass()) # Rather than using the default, pass in an
                                   # instance of your custom service class.

service = myAPI.getApp() # Get a reference to the Klein app. You can also call
                         # `getResource()` to get a Resource, if you want that
                         # instead!
service.run("127.0.0.1", 8094) # Start up a HTTP server using Klein's helper.
