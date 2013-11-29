#!/usr/bin/python

from haddock import API



class APIExample(object):

    class v1(object):

        def __init__(self, outer):
            pass

        @staticmethod
        def api_getWeather(config, request, params):

            return "weather v1"

        @staticmethod
        def api_getMail(config, request, params):

            return "mail v1 and 2"

    class v2(object):

        def __init__(self, outer):

            self.api_getMail = outer.v1.api_getMail

        @staticmethod
        def api_getWeather(config, request, params):

            return repr(params)


myAPI = API(APIExample, "exampleAPI.json")
app = myAPI.getApp()
app.run("127.0.0.1", 8094)