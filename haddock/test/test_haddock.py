from twisted.trial import unittest

import haddock.test.requestMock as rm

import haddock
import haddock.api
import inspect
import exceptions
import json
import os


class HaddockDefaultServiceClassTests(unittest.TestCase):
    """
    Haddock tests using the built in (blank) Default Service Class.
    """
    def setUp(self):
        path = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'exampleAPI.json')
        config = json.load(open(path))

        self.api = haddock.API(APIExample, config)


    def test_createdStructure(self):

        res = inspect.getmembers(self.api.service, predicate=inspect.isfunction)
        functions = []
        
        for item in res:
            functions.append(item[0])

        self.assertIn("api_v1_getMail", functions)
        self.assertIn("api_v2_getMail", functions)
        self.assertIn("api_v1_getWeather", functions)
        self.assertIn("api_v2_getWeather", functions)


    def test_blankServiceClass(self):

        def _cb(result):

            [error] = self.flushLoggedErrors()

            self.assertIsInstance(error.value, AttributeError)
            self.assertIsInstance(result.value, rm.HaddockAPIError)

        return rm.testItem(self.api.service.api_v1_getMail,
            "/v1/mail", {"to": "me"}).addBoth(_cb)



class HaddockExampleServiceClassTests(unittest.TestCase):
    """
    Haddock tests using ExampleServiceClass, an example for a user-specified
    Service Class.
    """
    def setUp(self):
        path = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'exampleAPI.json')
        config = json.load(open(path))

        self.api = haddock.API(APIExample, config,
            serviceObject=ExampleServiceClass())

    def test_usesServiceClass(self):

        def _cb(result):

            [error] = self.flushLoggedErrors()

            self.assertIsInstance(error.value, AttributeError)
            self.assertIsInstance(result.value, rm.HaddockAPIError)

        return rm.testItem(self.api.service.api_v1_getMail,
            "/v1/mail", {"to": "me"}).addBoth(_cb)



class ExampleServiceClass(object):

    def doSomething(self):
        return {"temperature": 30, "windSpeed": 20, "isRaining": False}



class APIExample(object):

    class v1(object):

        def __init__(self, outer):
            pass

        @staticmethod
        def api_getWeather(config, request, params):

            return config.doSomething()

        @staticmethod
        def api_getMail(config, request, params):

            return [{
                "from": "you",
                "to": "me",
                "subject": "hello",
                "sentTimestamp": 1386679094.0,
                "content": "hi there!"
            }]

    class v2(object):

        def __init__(self, outer):

            self.api_getMail = outer.v1.api_getMail

        @staticmethod
        def api_getWeather(config, request, params):

            return {"temperature": 30, "windSpeed": 20, "isRaining": False}
