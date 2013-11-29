from klein import Klein

import json


class API(object):

	def __init__(self, APIClass, configPath):

		self.app = Klein()
		self.config = json.load(open(configPath))

		print self.config

		versions = self.config["metadata"]["versions"]

		for version in versions:

			if hasattr(APIClass, "v%s" % (version,)):
				APIVersion = getattr(APIClass, "v%s" % (version))
			else:
				raise Exception("No v%s" % (version,))

			for api in self.config["api"]:

				for processor in api["processors"]:

					print processor



