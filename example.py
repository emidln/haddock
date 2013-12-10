#!/usr/bin/python

import json

from haddock import API
from haddock.test.test_haddock import APIExample

myAPI = API(APIExample, json.load(open("haddock/test/exampleAPI.json")))
service = myAPI.getService()
service.app.run("127.0.0.1", 8094)
