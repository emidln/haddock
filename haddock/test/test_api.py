from twisted.trial import unittest
from twisted.web.resource import Resource

from klein import Klein
from klein.resource import KleinResource

import haddock.test.requestMock as rm

from haddock.api import DefaultServiceClass

import haddock
import haddock.api
import haddock.auth

import inspect
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
        self.config = json.load(open(path))

        self.api = haddock.api.API(
            APIExample, self.config, serviceClass=myServiceClass())


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
        self.assertIn("api_vROOT_motd_GET", functions)


    def test_blankServiceClass(self):

        def _cb(result):

            [error] = self.flushLoggedErrors()
            self.assertIsInstance(error.value, AttributeError)

        return rm.testItem(
            self.api.getService().api_v1_weather_GET,"/v1/weather",
            {"postcode": "9999", "unixTimestamp": "1"}).addBoth(_cb)


    def test_requiredParam(self):

        def _cb(result):

            expectedResult = json.dumps(json.loads("""
                {"status": "fail",
                "data": "Missing request parameters: \'postcode\'"}
            """))
            self.assertEqual(expectedResult, result)

        return rm.testItem(
            self.api.getService().api_v1_weather_GET, "/v1/weather",
            {"unixTimestamp": "1"}).addBoth(_cb)


    def test_nonSpecifiedParam(self):

        def _cb(result):

            expectedResult = json.dumps(json.loads("""
                {"status": "fail",
                "data": "Unexpected request parameters: \'muffin\'"}
            """))
            self.assertEqual(expectedResult, result)

        return rm.testItem(
            self.api.getService().api_v1_weather_GET, "/v1/weather",
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

        return rm.testItem(
            self.api.getService().api_v2_motd_POST, "/v2/motd/POST",
            params, method="POST", useBody=True).addBoth(_cb)


    def test_missingFunction(self):

        try:
            self.api = haddock.api.API(
                MissingVersionFunctionAPIExample, self.config)
        except Exception, e:
            self.assertIsInstance(e, haddock.api.MissingHaddockAPIFunction)


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


    def test_rootAPI(self):

        def _cb(result):

            expectedResult = json.dumps(json.loads("""
                {"status": "success", "data": {"message": "a",
                "setBy": "a", "setWhen": 0}}
            """))
            self.assertEqual(expectedResult, result)

        return rm.testItem(self.api.getService().api_vROOT_motd_GET,
            "/motd", {}).addBoth(_cb)


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

        return rm.testItem(
            self.api.getService().api_v1_motd_POST, "/v1/motd/POST",
            params, method="POST", useBody=True).addBoth(_cb)


    def test_authRequired(self):

        def _cb(result):

            expectedResult = json.dumps(json.loads("""
                {"status": "fail", "data": "Authentication required."}
            """))
            self.assertEqual(expectedResult, result)

        return rm.testItem(
            self.api.getService().api_v1_authtest_GET, "/v1/authtest", {}
            ).addBoth(_cb)


    def test_authSuccess(self):

        def _cb(result):

            expectedResult = json.dumps(json.loads("""
                {"status": "success",
                "data": {"canonicalUsername": "aladdin@arug.net"}}
            """))
            self.assertEqual(expectedResult, result)

        return rm.testItem(self.api.getService().api_v1_authtest_GET,
            "/v1/authtest", {},
            headers={"Authorization": ["Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ=="]}
            ).addBoth(_cb)


    def test_authFailure(self):

        def _cb(result):

            expectedResult = json.dumps(json.loads("""
                {"status": "fail", "data": "Authentication failed."}
            """))
            self.assertEqual(expectedResult, result)

        return rm.testItem(self.api.getService().api_v1_authtest_GET,
            "/v1/authtest", {},
            headers={"Authorization": ["Basic QZxaZGRpbjpvcGVuIHNlc2FtZQ=="]}
            ).addBoth(_cb)


    def test_cors(self):

        resource = KleinResource(self.api.getApp())
        request = rm.requestMock("/", method="OPTIONS")
        result = resource.render(request)

        self.assertEqual(repr(request.setHeader.mock_calls), "[call('Access-Con\
trol-Allow-Origin', '*'),\n call('Access-Control-Allow-Methods', 'GET, POST'),\
\n call('Access-Control-Allow-Headers', 'authorization')]")


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

        return rm.testItem(
            self.api.getService().api_v1_weather_GET, "/v1/weather",
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


    def test_authFailureByDefault(self):

        def _cb(result):

            expectedResult = json.dumps(json.loads("""
                {"status": "fail", "data": "Not a real authenticator."}
            """))
            self.assertEqual(expectedResult, result)

        return rm.testItem(self.api.getService().api_v1_authtest_GET,
            "/v1/authtest", {},
            headers={"Authorization": ["Basic QZxaZGRpbjpvcGVuIHNlc2FtZQ=="]}
            ).addBoth(_cb)


    def test_getService(self):

        service = self.api.getService()
        self.assertIsInstance(service, ExampleServiceClass)



class HaddockBlankServiceClassTests(unittest.TestCase):
    """
    Haddock tests using CompletelyBlankServiceClass, a blank class that is
    passed in.
    """
    def setUp(self):
        path = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'betterAPI.json')
        config = json.load(open(path))

        self.api = haddock.api.API(APIExample, config,
            serviceClass=CompletelyBlankServiceClass())


    def test_getApp(self):

        app = self.api.getApp()
        self.assertIsInstance(app, Klein)



class ExampleServiceClass(DefaultServiceClass):

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

        def authtest_GET(service, request, params):
            return {"canonicalUsername": params["haddockAuth"]}


    class v2(object):

        def motd_GET(service, request, params):

            return [service.motd]

        def weather_GET(service, request, params):

            return {"temperature": 30, "windSpeed": 20, "isRaining": "YES"}

        def motd_POST(service, request, params):

            return json.dumps({"status": "BRILLIANT"})


    class vROOT(object):
        def motd_GET(service, request, params):
            return {"message":"a", "setBy": "a", "setWhen": 0}



class MissingVersionFunctionAPIExample(object):
    class v1(object):
        def weather_GET(service, request, params):
            """"""

        def motd_GET(service, request, params):
            """"""

        def motd_POST(service, request, params):
            """"""

        def authtest_GET(service, request, params):
            """"""

    class v2(object):
        def __init__(self, outer):
            self.motd_GET = outer.v1.motd_GET

        def weather_GET(service, request, params):
            """"""



class MissingVersionClassAPIExample(object):
    class v1(object):
        def weather_GET(service, request, params):
            """"""

        def motd_GET(service, request, params):
            """"""

        def motd_POST(service, request, params):
            """"""

        def authtest_GET(service, request, params):
            """"""



class myServiceClass(DefaultServiceClass):

    users = [{
        "username": "Aladdin",
        "canonicalUsername": "aladdin@arug.net",
        "password": "open sesame"
    }]

    auth = haddock.auth.DefaultHaddockAuthenticator(
        haddock.auth.InMemoryStringSharedSecretSource(users))

