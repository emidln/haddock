from haddock.info import apiInfo

from klein import Klein

from functools import wraps, update_wrapper

from twisted.python import log
from twisted.python.failure import Failure
from twisted.internet.defer import maybeDeferred

from jinja2 import Environment, PackageLoader

from copy import copy

import inspect
import json


class _DefaultServiceClass(object):
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
    def __init__(self, APIClass, config, serviceClass=None):
        """
        Initialise a Haddock API.

        @param APIClass: The class that contains the API functions.
        @param config: The Haddock API definition configuration L{dict}.
        @param serviceClass: A custom Service Class that contains your app's
        configuration and other functions.
        """
        self.config = config
        if not serviceClass:
            self.service = _DefaultServiceClass()
        else:
            self.service = serviceClass
        self.service.app = Klein()

        showAPIInfo = self.config["metadata"].get("apiInfo", False)

        if showAPIInfo:
            self.jEnv = Environment(loader=PackageLoader('haddock', 'static'))

        for version in self.config["metadata"]["versions"]:

            apiInfoData = []

            if hasattr(APIClass, "v%s" % (version,)):
                APIVersion = getattr(APIClass, "v%s" % (version))(APIClass)
            else:
                raise Exception("No v%s" % (version,))

            for api in self.config["api"]:

                apiProcessors = []

                for processor in api.get("getProcessors", []):
                    createRoute(self.service, version, processor, api, APIVersion, apiProcessors, "GET")

                for processor in api.get("postProcessors", []):
                    createRoute(self.service, version, processor, api, APIVersion, apiProcessors, "POST")

                if showAPIInfo:
                    apiLocal = copy(api)
                    apiLocal.pop("getProcessors", None)
                    apiLocal.pop("postProcessors", None)
                    apiInfoData.append((apiLocal, apiProcessors))

            if showAPIInfo:
                args = ["/v%s/apiInfo" % (version,)]
                kwargs = {"methods": ["GET"]}
                route = _makeRoute(self.service, apiInfo, args, kwargs, None, [apiInfoData, self.jEnv, version])
                setattr(self.service, "apiInfo_v%s" % (version,), route)


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


def createRoute(service, version, processor, api, APIVersion, apiProcessors, HTTPType):

    endpointLoc = "/v%s/%s" % (version, api["endpoint"])
    newFuncName = str("api_v%s_%s_%s" % (version, api["name"], HTTPType))

    if hasattr(APIVersion, "%s_%s" % (api["name"], HTTPType)):
        APIFunc = getattr(APIVersion, "%s_%s" % (api["name"], HTTPType))
        APIFunc.__name__ = newFuncName
    else:
        raise Exception("no %s_%s in v%s" % (api["name"], HTTPType, version))

    if version in processor["versions"]:

        apiProcessors.append(processor)

        args = [endpointLoc]
        kwargs = {"methods": [HTTPType]}

        route = _makeRoute(
            service, APIFunc, args, kwargs, processor, None)
        setattr(service, newFuncName, route)


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


def _makeRoute(serviceClass, method, args, kw, APIInfo, overrideParams):

    @wraps(method)
    def wrapper(*args, **kw):
        return _setup(method, serviceClass, APIInfo, args[0], overrideParams, *args, **kw)

    update_wrapper(wrapper, method)
    route = serviceClass.app.route(*args, **kw)

    return route(wrapper)


def _setup(func, self, APIInfo, request, overrideParams, *args, **kw):

    try:
        d = _setupWrapper(func, self, APIInfo, request, overrideParams, *args, **kw)
        d.addErrback(_handleAPIError, request)
        return d
    except Exception as exp:
        return _handleAPIError(Failure(), request)


def _setupWrapper(func, self, APIInfo, request, overrideParams, *args, **kw):

    if not overrideParams:

        params = None
        paramsType = APIInfo.get("paramsType", "url")

        if paramsType == "url":
            params = _getParams(request.args, APIInfo)
        elif paramsType == "jsonbody":
            requestContent = json.loads(request.content.read())
            params = _getParams(params, APIInfo)

        d = maybeDeferred(func, self, request, params)        
        d.addErrback(_handleAPIError, request)

        if APIInfo.get("returnParams"):
            d.addCallback(_verifyReturnParams, APIInfo)
            d.addErrback(_handleAPIError, request)

        d.addCallback(_formatResponse, request)

        return d

    else:

        d = maybeDeferred(func, self, request, overrideParams)
        return d


def _verifyReturnParams(result, APIInfo):

    returnFormat = APIInfo.get("returnFormat", "dict")

    if returnFormat == "dict":

        if isinstance(result, basestring):
            keys = set(json.loads(result).keys())
        else:
            keys = set(result.keys())

        if not isinstance(result, dict):
            raise BadResponseParams("Result did not match the return format.")

        _checkReturnParamsDict(result, APIInfo)

    elif returnFormat == "list":

        if isinstance(result, basestring):
            items = json.loads(result)
        else:
            items = result

        if not isinstance(items, list):
            raise BadResponseParams("Result did not match the return format.")

        for item in items:
            _checkReturnParamsDict(item, APIInfo)

    return result


def _checkReturnParamsDict(result, APIInfo):

    requiredInput = APIInfo.get("returnParams", set())

    requiredKeys = []
    accountedFor = []
    required = []

    for req in requiredInput:
        if isinstance(req, dict):
            options = []
            if req.get("paramOptions", None):
                for option in req.get("paramOptions", None):
                    if isinstance(option, dict):
                        options.append(option["data"])
                    elif isinstance(option, basestring):
                        options.append(option)

            requiredKeys.append(req["param"])
            required.append({
                "param": req["param"],
                "paramOptions": options
            })
        elif isinstance(req, basestring):
            requiredKeys.append(req)
            required.append({
                "param": req,
            })

    for key, data in result.iteritems():
        for req in required:
            if req["param"] == key:
                if req.get("paramOptions", None):
                    if not data in options:
                        raise BadResponseParams("%s is not part of %s in %s" % (data, repr(options), key))

                accountedFor.append(req["param"])

    missing = set(requiredKeys) - set(accountedFor)

    extra = None # FIXME






    if missing:
        raise BadResponseParams("Missing response parameters: '%s'" % (
            "', '".join(sorted(missing))))
    if extra:
        raise BadResponseParams("Unexpected response parameters: '%s'" % (
            "', '".join(sorted(extra))))


def _getParams(params, APIInfo):

    if params:
        keys = set(params.keys())
    else:
        keys = set()

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

    if request.finished:
        # If we've already hit an error, don't return any more.
        return

    error = failure.value
    errorcode = 500

    if not isinstance(error, BadRequestParams):
        log.err(failure)
    if hasattr(error, "code"):
        errorcode = error.code

    request.setHeader('Content-Type', 'application/json')

    request.setResponseCode(errorcode)

    if errorcode == 500:
        errstatus = "error"
        errmessage = "Internal server error."
    else:
        errstatus = "fail"
        errmessage = error.message

    response = {
        "status": errstatus,
        "data": errmessage
    }

    request.write(json.dumps(response))
    request.finish()
    return json.dumps(response)



def _formatResponse(result, request):

    if request.finished:
        # If we've hit an error, we can't return data, because we've already
        # shut the connection.
        return

    request.setHeader('Content-Type', 'application/json')

    response = {
        "status": "success",
        "data": result
    }

    return json.dumps(response)
