#!/usr/bin/python

# Import API (which assembles the API) and the DefaultServiceClass that you can
# use as the base for your service class.
from haddock.api import API, DefaultServiceClass
import json

class myServiceClass(DefaultServiceClass):
    def __init__(self):
        # Store things in your service class that you want to access in your
        # API's methods.
        self.motd = {
            "message": "NO MOTD SET",
            "setBy": "nobody",
            "setWhen": 0
        }

    def doSomething(self):
        # An example function, called from the inside of the API example.
        return {"temperature": 30, "windSpeed": 20, "isRaining": False}


class APIExample(object):
    class v1(object):
        def __init__(self, outer):
            # `outer` is actually the a reference to the master `APIExample`.
            pass

        @staticmethod
        def weather_GET(service, request, params):
            # Call a method on your service class.
            return service.doSomething()

    class v2(object):
        def __init__(self, outer):
            # `outer` is actually the a reference to the master `APIExample`.
            pass

        @staticmethod
        def weather_GET(service, request, params):
            # Return an object - Haddock will check it according to your API
            # definition and JSONise it.
            return {"temperature": 30, "windSpeed": 20, "isRaining": "YES"}


myAPI = API(
    APIExample, # Pass in your API class.
    json.load(open("APIExample.json")), # Load your API definition and pass it in.
    serviceClass=myServiceClass()) # Rather than using the default, pass in an
                                   # instance to your custom service class.

service = myAPI.getApp() # Get a reference to the Klein backbone.
service.run("127.0.0.1", 8094) # Start up a HTTP server!
