from twisted.trial import unittest
from twisted.web.resource import Resource

from klein import Klein
from twisted.web.static import File

import haddock.test.requestMock as rm

import haddock
import haddock.api
import inspect
import exceptions
import json
import traceback
import time
import os
import sys



class HaddockDefaultServiceClassTests(unittest.TestCase):
    """
    Haddock tests using the built in (blank) Default Service Class.
    """
    def setUp(self):
        path = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'betterAPI.json')
        self.config = json.load(open(path))

        self.api = haddock.api.API(APIExample, self.config)


    def test_createdStructure(self):

        res = inspect.getmembers(
            self.api.getService(), predicate=inspect.isfunction)
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

        return rm.testItem(self.api.getService().api_v1_weather_GET, "/v1/weather",
            {"postcode": "9999", "unixTimestamp": "1"}).addBoth(_cb)


    def test_requiredParam(self):

        def _cb(result):

            expectedResult = json.dumps(json.loads("""
                {"status": "fail",
                "data": "Missing request parameters: \'postcode\'"}
            """))
            self.assertEqual(expectedResult, result)

        return rm.testItem(self.api.getService().api_v1_weather_GET, "/v1/weather",
            {"unixTimestamp": "1"}).addBoth(_cb)


    def test_nonSpecifiedParam(self):

        def _cb(result):

            expectedResult = json.dumps(json.loads("""
                {"status": "fail",
                "data": "Unexpected request parameters: \'muffin\'"}
            """))
            self.assertEqual(expectedResult, result)

        return rm.testItem(self.api.getService().api_v1_weather_GET, "/v1/weather",
            {"postcode": "9999", "unixTimestamp": "1", "muffin": "yes plz"}
            ).addBoth(_cb)


    def test_incorrectParamReturn(self):

        def _cb(result):

            [error] = self.flushLoggedErrors()
            self.assertIsInstance(error.value, haddock.api.BadResponseParams)

        params = {
            "message": "hi",
            "username": "hawkowl"
        }

        return rm.testItem(self.api.getService().api_v2_motd_POST, "/v2/motd/POST",
            params, method="POST", useBody=True).addBoth(_cb)


    def test_missingFunction(self):

        try:
            self.api = haddock.api.API(
                MissingVersionFunctionAPIExample, self.config)
        except Exception, e:
            self.assertIsInstance(e, haddock.api.MissingHaddockAPIFunction)
        else:
            self.fail()


    def test_missingClass(self):

        try:
            self.api = haddock.api.API(
                MissingVersionClassAPIExample, self.config)
        except Exception, e:
            self.assertIsInstance(e, haddock.api.MissingHaddockAPIVersionClass)


    def test_APIDocs(self):

        def _cb(result):

            expectedResult = "<title>API Information for v1</title>"
            self.assertSubstring(expectedResult, result)

        return rm.testItem(self.api.getService().apiInfo_v1, "/v1/apiInfo",{}
            ).addBoth(_cb)


    def test_jsonBody(self):

        def _cb(result):

            expectedResult = json.dumps(json.loads("""
                {"status": "success",
                "data": {"status": "OK"}}
            """))
            self.assertEqual(expectedResult, result)

        params = {
            "message": "hi",
            "username": "hawkowl"
        }

        return rm.testItem(self.api.getService().api_v1_motd_POST, "/v1/motd/POST",
            params, method="POST", useBody=True).addBoth(_cb)


    def test_getService(self):

        service = self.api.getService()
        self.assertIsInstance(service, haddock.api.DefaultServiceClass)
    

    def test_getResource(self):

        resource = self.api.getResource()
        self.assertIsInstance(resource, Resource)


    def test_getApp(self):

        app = self.api.getApp()
        self.assertIsInstance(app, Klein)



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
                {"status": "success", "data": {
                "windSpeed": 20, "temperature": 30, "isRaining": false}}
            """))
            self.assertEqual(expectedResult, result)

        return rm.testItem(self.api.getService().api_v1_weather_GET, "/v1/weather",
            {"postcode": "9999", "unixTimestamp": "1"}).addBoth(_cb)


    def test_returnList(self):

        def _cb(result):

            expectedResult = json.dumps(json.loads("""
                {"status": "success",
                "data": [{"message": "NO MOTD SET",
                "setBy": "nobody", "setWhen": 0}]}
            """))
            self.assertEqual(expectedResult, result)

        return rm.testItem(self.api.getService().api_v2_motd_GET, "/v2/motd",
            {}).addBoth(_cb)


    def test_getService(self):

        service = self.api.getService()
        self.assertIsInstance(service, ExampleServiceClass)


class ExampleServiceClass(object):

    app = Klein()

    @app.route("/content", branch=True)
    def _staticFile(self, request):

        return File(os.path.join(haddock.basePath, "static", "content"))

    def __init__(self):

        self.motd = {
            "message": "NO MOTD SET",
            "setBy": "nobody",
            "setWhen": 0
        }

    def doSomething(self):
        return {"temperature": 30, "windSpeed": 20, "isRaining": False}


class CompletelyBlankServiceClass(object):
    pass



class APIExample(object):
    class v1(object):
        def __init__(self, outer):
            pass

        def weather_GET(service, request, params):

            return service.doSomething()

        def motd_GET(service, request, params):

            return service.motd

        def motd_POST(service, request, params):

            service.motd = {
                "message": params["message"],
                "setBy": params["username"],
                "setWhen": time.time()
            }

            return {"status": "OK"}

    class v2(object):
        def __init__(self, outer):
            pass

        def motd_GET(service, request, params):

            return [service.motd]

        def weather_GET(service, request, params):

            return {"temperature": 30, "windSpeed": 20, "isRaining": "YES"}

        def motd_POST(service, request, params):

            return json.dumps({"status": "BRILLIANT"})


class MissingVersionFunctionAPIExample(object):
    class v1(object):
        def __init__(self, outer):
            pass

        def weather_GET(service, request, params):

            return service.doSomething()

        def motd_GET(service, request, params):

            return service.motd

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

        def weather_GET(service, request, params):

            return {"temperature": 30, "windSpeed": 20, "isRaining": "YES"}


class MissingVersionClassAPIExample(object):
    class v1(object):
        def __init__(self, outer):
            pass

        def weather_GET(service, request, params):

            return service.doSomething()

        def motd_GET(service, request, params):

            return service.motd

        def motd_POST(service, request, params):

            service.motd = {
                "message": params["message"],
                "setBy": params["username"],
                "setWhen": time.time()
            }

            return {"status": "OK"}