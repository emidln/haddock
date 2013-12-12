from jinja2 import Environment, PackageLoader

def apiInfo(self, versionName, APIs):

	return repr([self, versionName, APIs])