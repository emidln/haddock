from haddock import API



class HawkOwlAPIExample(object):

	class v1(object):

		def api_getWeather(self, request):

			print repr(self)

		def api_getMail(self, request):

			print repr(self)

	class v2(object):

		def api_getWeather(self, request):

			print repr(self)

		self.api_getMail = HawkOwlAPIExample.v1.api_getMail


myAPI = API(HawkOwlAPIExample, "exampleAPI.json")