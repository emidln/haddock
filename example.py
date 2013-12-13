#!/usr/bin/python

import json

from haddock.api import API
from haddock.test.test_haddock import APIExample, ExampleServiceClass

myAPI = API(APIExample, json.load(open("haddock/test/betterAPI.json")), serviceClass=ExampleServiceClass())
service = myAPI.getService()
service.app.run("127.0.0.1", 8094)
