from klein import Klein

from functools import wraps, update_wrapper
from twisted.internet.defer import maybeDeferred

import inspect

import json

class ServiceObject(object):
    """
    Service object!
    """


class API(object):

    def __init__(self, APIClass, configPath):

        self.config = json.load(open(configPath))
        self.service = ServiceObject()
        self.service.app = Klein()

        versions = self.config["metadata"]["versions"]

        for version in versions:

            if hasattr(APIClass, "v%s" % (version,)):
                APIVersion = getattr(APIClass, "v%s" % (version))(APIClass)
            else:
                raise Exception("No v%s" % (version,))

            for api in self.config["api"]:

                for processor in api["processors"]:

                    if hasattr(APIVersion, "api_%s" % (api["name"],)):
                        APIFunc = getattr(APIVersion, "api_%s" % (api["name"],))
                        APIFunc.__name__ = str("api_v%s_%s" % (version,
                            api["name"]))
                    else:
                        raise Exception("no %s in v%s" % (api["name"], version))

                    if version in processor["versions"]:

                        args = ["/v%s/%s" % (version, processor["endpoint"])]
                        kwargs = {"methods": api["allowedMethods"]}

                        handler = _makeRoute(
                            self.service, APIFunc, args, kwargs, processor)
                        setattr(self.service,
                            "api_v%s_%s" % (version, api["name"]), handler)


    def getService(self):

        return self.service.app.resource()


    def getApp(self):

        return self.service.app


# The code below is partially based on the equiv in Praekelt's Aludel

class APIError(Exception):
    code = 500

    def __init__(self, message, code=None):
        super(APIError, self).__init__(message)
        if code is not None:
            self.code = code


class BadRequestParams(APIError):
    code = 400

def _makeRoute(serviceClass, method, args, kw, APIInfo):

    @wraps(method)
    def wrapper(*args, **kw):
        return _setupWrapper(method, serviceClass, APIInfo, *args, **kw)

    update_wrapper(wrapper, method)
    route = serviceClass.app.route(*args, **kw)

    return route(wrapper)

def _setupWrapper(func, self, APIInfo, request, *args, **kw):

    params = None
    paramsType = APIInfo.get("paramsType", "url")

    if paramsType == "url":

        params = _getParams(request.args, APIInfo)
        params = dict((k, v[0]) for k, v in params.iteritems())

    elif paramsType == "jsonbody":

        requestContent = json.loads(request.content.read())
        params = _getParams(params, APIInfo)


    d = maybeDeferred(func, self, request, params)
    #d.addCallback(format_response, request)
    #if hasattr(self, 'handle_api_error'):
    #    d.addErrback(self.handle_api_error, request)
    #d.addErrback(_handle_api_error, request)
    return d

def _getParams(params, APIInfo):

    keys = set(params.keys())
    required = set(APIInfo.get("requiredParams", set()))
    optional = set(APIInfo.get("optionalParams", set()))

    missing = required - keys
    extra = keys - (required | optional)

    if missing:
        raise BadRequestParams("Missing request parameters: '%s'" % (
            "', '".join(sorted(missing))))
    if extra:
        raise BadRequestParams("Unexpected request parameters: '%s'" % (
            "', '".join(sorted(extra))))

    return params