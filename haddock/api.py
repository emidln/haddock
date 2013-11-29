from klein import Klein

from functools import wraps, update_wrapper

from twisted.python import log
from twisted.python.failure import Failure
from twisted.internet.defer import maybeDeferred

import inspect

import json

class ServiceObject(object):
    """
    Service object!

    @ivar app: A L{Klein} app.
    """


class API(object):
    """
    A Haddock API object.

    @ivar config: The API description language configuration.
    @ivar service: The class that Haddock puts everything into.
    """

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

                    endpointLoc = "/v%s/%s" % (version, processor["endpoint"])
                    newFuncName = str("api_v%s_%s" % (version, api["name"]))

                    if hasattr(APIVersion, "api_%s" % (api["name"],)):
                        APIFunc = getattr(APIVersion, "api_%s" % (api["name"],))
                        APIFunc.__name__ = newFuncName
                    else:
                        raise Exception("no %s in v%s" % (api["name"], version))

                    if version in processor["versions"]:

                        args = [endpointLoc]
                        kwargs = {"methods": api["allowedMethods"]}

                        route = _makeRoute(
                            self.service, APIFunc, args, kwargs, processor)
                        setattr(self.service, newFuncName, route)


    def getService(self):
        """
        Returns the service object.
        """
        return self.service


    def getResource(self):
        """
        Returns a Resource, from the Klein app.
        """
        return self.service.app.resource()

    def getApp(self):
        """
        Returns the Klein app.
        """
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

class BadResponseParams(APIError):
    code = 500


def _makeRoute(serviceClass, method, args, kw, APIInfo):

    @wraps(method)
    def wrapper(*args, **kw):
        return _setup(method, serviceClass, APIInfo, *args, **kw)

    update_wrapper(wrapper, method)
    route = serviceClass.app.route(*args, **kw)

    return route(wrapper)


def _setup(func, self, APIInfo, request, *args, **kw):

    try:
        d = _setupWrapper(func, self, APIInfo, request, *args, **kw)
        d.addErrback(_handleAPIError, request)
        return d
    except Exception as exp:
        return _handleAPIError(Failure(), request)


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

    if APIInfo.get("returnParams"):
        d.addCallback(_verifyReturnParams, APIInfo)

    d.addCallback(_formatResponse, request)

    return d


def _verifyReturnParams(result, APIInfo):

    keys = set(result.keys())
    required = set(APIInfo.get("returnParams", set()))
    optional = set(APIInfo.get("optionalReturnParams", set()))

    missing = required - keys
    extra = keys - (required | optional)

    if missing:
        raise BadResponseParams("Missing response parameters: '%s'" % (
            "', '".join(sorted(missing))))
    if extra:
        raise BadResponseParams("Unexpected response parameters: '%s'" % (
            "', '".join(sorted(extra))))

    return result


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


def _handleAPIError(failure, request):

    error = failure.value
    if not failure.check(APIError):
        log.err(failure)
        error = APIError('Internal server error.')

    request.setHeader('Content-Type', 'application/json')
    request.setResponseCode(error.code)
    return json.dumps({
        'error': error.message,
    })


def _formatResponse(result, request):

    request.setHeader('Content-Type', 'application/json')
    return json.dumps(result)
