from klein import Klein

from functools import wraps, update_wrapper

from twisted.python import log
from twisted.web.http import Request
from twisted.python.failure import Failure
from twisted.internet.defer import maybeDeferred
from twisted.web.static import File

from jinja2 import Environment, PackageLoader

from copy import copy

import inspect
import json
import os, sys, traceback


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

class MissingHaddockAPIFunction(Exception):
    pass

class MissingHaddockAPIVersionClass(Exception):
    pass


class DefaultServiceClass(object):
    """
    Service object!

    @ivar app: A L{Klein} app.
    """
    app = Klein()

    @app.route("/content", branch=True)
    def _staticFile(self, request):

        return File(os.path.join(os.path.abspath(
            os.path.dirname(__file__)), "static", "content"))


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
            self.serviceClass = DefaultServiceClass()
        else:
            self.serviceClass = serviceClass

        if not hasattr(self.serviceClass, "app"):
            self.serviceClass.app = Klein()

        showAPIInfo = self.config["metadata"].get("apiInfo", False)

        if showAPIInfo:
            self.jEnv = Environment(loader=PackageLoader('haddock', 'static'))

        for version in self.config["metadata"]["versions"]:
            apiInfoData = []

            if hasattr(APIClass, "v%s" % (version,)):
                APIVersion = getattr(APIClass, "v%s" % (version))(APIClass)
            else:
                raise MissingHaddockAPIVersionClass("No v%s" % (version,))

            for api in self.config["api"]:
                apiProcessors = []

                for processor in api.get("getProcessors", []):
                    _createRoutes(
                        self.serviceClass, APIVersion, version, "GET",
                        apiProcessors, self.config["metadata"], api, processor)

                for processor in api.get("postProcessors", []):
                    _createRoutes(
                        self.serviceClass, APIVersion, version, "POST",
                        apiProcessors, self.config["metadata"], api, processor)

                if showAPIInfo:
                    apiLocal = copy(api)
                    apiLocal.pop("getProcessors", None)
                    apiLocal.pop("postProcessors", None)
                    apiInfoData.append((apiLocal, apiProcessors))

            if showAPIInfo:
                if not version == "ROOT":
                    endpointPath = "/v%s/apiInfo" % (version,)
                else:
                    endpointPath = "/apiInfo"
                kwargs = {"methods": ["GET"]}
                apiInfo = copy(_apiInfo)
                apiInfo.__name__ = str("v%s_apiInfo" % (version,))

                route = _makeRoute(
                    self.serviceClass, apiInfo, endpointPath, kwargs,
                    [apiInfoData, self.jEnv, version, self.config["metadata"]],
                    self.config["metadata"], None, None)

                setattr(self.serviceClass, "apiInfo_v%s" % (version,), route)


    def getService(self):
        """
        Returns the service object.
        """
        return self.serviceClass


    def getResource(self):
        """
        Returns a Resource, from the Klein app.
        """
        return self.serviceClass.app.resource()


    def getApp(self):
        """
        Returns the Klein app.
        """
        return self.serviceClass.app


def _createRoutes(serviceClass, sourceClassVersion, APIVersion, HTTPType,
                  APIProcessorList, configMetadata, configAPI, configProcessor):
    """
    Creates the routes and puts them in the service.

    @param service: The service class to put the routes in.
    @param version: The version that we are taking the API methods from.
    @param API: The API we are currently working on, from the API configuration.
    @param APIProcessor: The processor we are currently working on from the API
    configuration.
    @param sourceClassVersion: The source class version we're currently working
    from.
    @param apiProcessors: For L{_apiInfo}.
    @param HTTPType: The HTTP type we are currently working with.
    """
    sourceClassLocation = "%s_%s" % (configAPI["name"], HTTPType)
    newFuncName = str("api_v%s_%s" % (APIVersion, sourceClassLocation))

    if not APIVersion == "ROOT":
        endpointLoc = "/v%s/%s" % (APIVersion, configAPI["endpoint"])
    else:
        endpointLoc = "/%s" % (configAPI["endpoint"],)

    if hasattr(sourceClassVersion, sourceClassLocation):
        APIFunc = copy(getattr(sourceClassVersion, sourceClassLocation).im_func)
        APIFunc.__name__ = newFuncName
    else:
        raise MissingHaddockAPIFunction(
            "no %s in v%s" % (sourceClassLocation, APIVersion))

    if APIVersion in configProcessor["versions"]:
        kwargs = {"methods": [HTTPType]}
        route = _makeRoute(serviceClass, APIFunc, endpointLoc, kwargs, None, 
            configMetadata, configAPI, configProcessor)

        setattr(serviceClass, newFuncName, route)
        APIProcessorList.append((configProcessor, HTTPType))


def _makeRoute(serviceClass, func, endpointPath, keywordArgs, overrideParams,
               configMetadata, configAPI, configProcessor):

    @wraps(func)
    def wrapper(*args, **kw):
        request = None
        for item in args:
            if isinstance(item, Request):
                request = item
                request.errored = False

        if configMetadata.get("cors"):
            request.setHeader(
                "Access-Control-Allow-Origin", str(configMetadata["cors"]))

        try:
            if not overrideParams:
                params = None
                paramsType = configProcessor.get("paramsType", "url")

                if paramsType == "url":
                    args = request.args
                    params = {}
                    for key, data in args.iteritems():
                        params[key] = data[0]
                    params = _getParams(params, configProcessor)
                elif paramsType == "jsonbody":
                    requestContent = request.content.read()
                    params = json.loads(requestContent)
                    params = _getParams(params, configProcessor)

                d = maybeDeferred(func, serviceClass, request, params)        
                d.addErrback(_handleAPIError, request)

                if configProcessor.get("returnParams"):
                    d.addCallback(_verifyReturnParams, configProcessor)
                    d.addErrback(_handleAPIError, request)

                d.addCallback(_formatResponse, request)
                return d
            else:
                return maybeDeferred(func, serviceClass, request, overrideParams)

        except Exception as exp:
            return _handleAPIError(Failure(exp), request)

    update_wrapper(wrapper, func)
    route = serviceClass.app.route(endpointPath, **keywordArgs)

    return route(wrapper)


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


def _normaliseParams(params):

    finishedParams = []
    paramKeys = []

    for param in params:
        if isinstance(param, dict):
            options = []
            if param.get("paramOptions", None):
                for option in param.get("paramOptions", None):
                    if isinstance(option, dict):
                        options.append(option["data"])
                    elif isinstance(option, basestring):
                        options.append(option)

            paramKeys.append(param["param"])
            finishedParams.append({
                "param": param["param"],
                "paramOptions": options
            })
        elif isinstance(param, basestring):
            paramKeys.append(param)
            finishedParams.append({
                "param": param,
            })

    return (finishedParams, set(paramKeys))


def _checkParamOptions(item, data, exp):

    paramOptions = item.get("paramOptions", None)

    if paramOptions and not data in paramOptions:
        raise exp("%s isn't part of %s in %s" % (data, repr(paramOptions), item))


def _checkReturnParamsDict(result, APIInfo):

    if result:
        keys = set(result.keys())
    else:
        keys = set()

    requiredInput = APIInfo.get("returnParams", set())
    optionalInput = APIInfo.get("optionalReturnParams", set())

    required, requiredKeys = _normaliseParams(requiredInput)
    optional, optionalKeys = _normaliseParams(optionalInput)
    accountedFor = set()

    for key, data in result.iteritems():
        for req in required + optional:
            if req["param"] == key:
                _checkParamOptions(req, data, BadResponseParams)
                accountedFor.add(req["param"])

    missing = requiredKeys - accountedFor
    extra = keys - (requiredKeys | optionalKeys)

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
        params = {}

    requiredInput = APIInfo.get("requiredParams", set())
    optionalInput = APIInfo.get("optionalParams", set())

    required, requiredKeys = _normaliseParams(requiredInput)
    optional, optionalKeys = _normaliseParams(optionalInput)
    accountedFor = set()

    for key, data in params.iteritems():
        for req in required + optional:
            if req["param"] == key:
                _checkParamOptions(req, data, BadRequestParams)
                accountedFor.add(req["param"])

    missing = requiredKeys - accountedFor
    extra = keys - (requiredKeys | optionalKeys)

    if missing:
        raise BadRequestParams("Missing request parameters: '%s'" % (
            "', '".join(sorted(missing))))
    if extra:
        raise BadRequestParams("Unexpected request parameters: '%s'" % (
            "', '".join(sorted(extra))))

    return params


def _handleAPIError(failure, request):

    if request.finished or request.errored:
        # If we've already hit an error, don't return any more.
        return

    error = failure.value
    errorcode = 500

    if not isinstance(error, BadRequestParams):
        traceback.print_exc(file=sys.stderr)
        log.err(error)
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

    request.errored = True
    return json.dumps(response)


def _formatResponse(result, request):

    if request.finished or request.errored:
        # If we've hit an error, we can't return data, because we've already
        # shut the connection.
        return

    request.setHeader('Content-Type', 'application/json')

    response = {
        "status": "success",
        "data": result
    }

    return json.dumps(response)


def _apiInfo(self, request, args):

    API, env, version, metadata = args

    return env.get_template("apiVersionInfo.html").render(APIs=API,
        version=version, metadata=metadata)