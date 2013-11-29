from haddock import API



class HawkOwlAPIExample(object):

	class v1(object):

		def __init__(self, outer):
			pass

		@staticmethod
		def api_getWeather(config, request):

			print repr(request)

		@staticmethod
		def api_getMail(config, request):

			print repr(request)

	class v2(object):

		def __init__(self, outer):

			self.api_getMail = outer.v1.api_getMail

		@staticmethod
		def api_getWeather(config, request):

			print repr(request)


myAPI = API(HawkOwlAPIExample, "exampleAPI.json")

h = HawkOwlAPIExample()
v = h.v2(h)
v.api_getMail("blah", "blah")