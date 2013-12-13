from twisted.trial import unittest

import haddock.test.requestMock as rm

import haddock.api
import inspect
import exceptions
import json
import time
import os


class HaddockDefaultServiceClassTests(unittest.TestCase):
    """
    Haddock tests using the built in (blank) Default Service Class.
    """
    def setUp(self):
        path = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'betterAPI.json')
        config = json.load(open(path))

        self.api = haddock.api.API(APIExample, config)


    def test_createdStructure(self):

        res = inspect.getmembers(self.api.service, predicate=inspect.isfunction)
        functions = []
        
        for item in res:
            functions.append(item[0])

        self.assertIn("api_v1_weather_GET", functions)
        self.assertIn("api_v2_weather_GET", functions)
        self.assertIn("api_v1_motd_GET", functions)
        self.assertIn("api_v2_motd_GET", functions)
        self.assertIn("api_v1_motd_POST", functions)
        self.assertIn("api_v2_motd_POST", functions)


    def test_blankServiceClass(self):

        def _cb(result):

            [error] = self.flushLoggedErrors()
            self.assertIsInstance(error.value, AttributeError)
            self.assertIsNone(result)

        return rm.testItem(self.api.service.api_v1_weather_GET, "/v1/weather",
            {"postcode": "9999", "unixTimestamp": "1"}).addBoth(_cb)



class HaddockExampleServiceClassTests(unittest.TestCase):
    """
    Haddock tests using ExampleServiceClass, an example for a user-specified
    Service Class.
    """
    def setUp(self):
        path = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'betterAPI.json')
        config = json.load(open(path))

        self.api = haddock.api.API(APIExample, config,
            serviceClass=ExampleServiceClass())

    def test_usesServiceClass(self):

        def _cb(result):

            expectedResult = json.dumps(json.loads("""
                {"status": "success", "data": {"windSpeed": 20, "temperature": 30, "isRaining": false}}
            """))
            self.assertEqual(expectedResult, result)

        return rm.testItem(self.api.service.api_v1_weather_GET, "/v1/weather",
            {"postcode": "9999", "unixTimestamp": "1"}).addBoth(_cb)



class ExampleServiceClass(object):

    def __init__(self):

        self.motd = {
            "message": "NO MOTD SET",
            "setBy": "nobody",
            "setWhen": 0
        }

    def doSomething(self):
        return {"temperature": 30, "windSpeed": 20, "isRaining": False}



class APIExample(object):

    class v1(object):

        def __init__(self, outer):
            pass

        @staticmethod
        def weather_GET(service, request, params):

            return service.doSomething()

        @staticmethod
        def motd_GET(service, request, params):

            return service.motd

        @staticmethod
        def motd_POST(service, request, params):

            service.motd = {
                "message": params["message"],
                "setBy": params["username"],
                "setWhen": time.time()
            }

            return {"status": "OK"}

    class v2(object):

        def __init__(self, outer):

            self.motd_GET = outer.v1.motd_GET

        @staticmethod
        def weather_GET(service, request, params):

            return {"temperature": 30, "windSpeed": 20, "isRaining": "YES"}

        @staticmethod
        def motd_POST(service, request, params):

            return {"status": "BRILLIANT"}
