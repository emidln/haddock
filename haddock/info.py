

def apiInfo(self, request, args):

	API, env, version = args

	return env.get_template("apiVersionInfo.html").render(APIs=API, version=version)