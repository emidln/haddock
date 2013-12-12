

def apiInfo(self, request, args):

	API, env = args

	return env.get_template("apiVersionInfo.html").render(APIs=API)