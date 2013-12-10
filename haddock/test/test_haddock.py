from twisted.trial import unittest

import haddock
import json
import os


class HaddockDefaultServiceObjTests(unittest.TestCase):

    def setUp(self):

        path = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'exampleAPI.json')
        config = json.load(open(path))

        self.api = haddock.API(APIExample, config)

    def test_createdStructure(self):

        print repr(self.api)



class APIExample(object):

    class v1(object):

        def __init__(self, outer):
            pass

        @staticmethod
        def api_getWeather(config, request, params):

            return "I will break!"

        @staticmethod
        def api_getMail(config, request, params):

            return "mail v1 and 2"

    class v2(object):

        def __init__(self, outer):

            self.api_getMail = outer.v1.api_getMail

        @staticmethod
        def api_getWeather(config, request, params):

            return {"temperature": 30, "windSpeed": 20, "isRaining": False}