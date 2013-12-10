#!/usr/bin/python

from haddock import API
import json


class APIExample(object):

    class v1(object):

        def __init__(self, outer):
            pass

        @staticmethod
        def api_getWeather(config, request, params):

            return "I will break!"

        @staticmethod
        def api_getMail(config, request, params):

            return [{

                "from": "you",
                "to": "me",
                "subject": "hello",
                "sentTimestamp": 1386679094.0

            }]

    class v2(object):

        def __init__(self, outer):

            self.api_getMail = outer.v1.api_getMail

        @staticmethod
        def api_getWeather(config, request, params):

            return {"temperature": 30, "windSpeed": 20, "isRaining": False}



myAPI = API(APIExample, json.load(open("haddock/test/exampleAPI.json")))
service = myAPI.getService()
service.app.run("127.0.0.1", 8094)
