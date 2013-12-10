from twisted.trial import unittest

import haddock.test.requestMock as rm

import haddock
import haddock.api
import inspect
import exceptions
import json
import os


class HaddockDefaultServiceObjTests(unittest.TestCase):


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





class ExampleServiceClass(object):

    def doSomething(self):
        return "test!"


class APIExample(object):

    class v1(object):

        def __init__(self, outer):
            pass

        @staticmethod
        def api_getWeather(config, request, params):

            return "I will break!"

        @staticmethod
        def api_getMail(config, request, params):

            return config.doSomething()

    class v2(object):

        def __init__(self, outer):

            self.api_getMail = outer.v1.api_getMail

        @staticmethod
        def api_getWeather(config, request, params):

            return {"temperature": 30, "windSpeed": 20, "isRaining": False}
