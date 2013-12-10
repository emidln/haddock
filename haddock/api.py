from klein import Klein

from functools import wraps, update_wrapper

from twisted.python import log
from twisted.python.failure import Failure
from twisted.internet.defer import maybeDeferred

import inspect
import json

class _DefaultServiceObject(object):
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


        """
        self.config = config
        if not serviceClass:
            self.service = _DefaultServiceObject()
        else:
            self.service = serviceClass
        self.service.app = Klein()

        for version in self.config["metadata"]["versions"]:

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
    elif paramsType == "jsonbody":
        requestContent = json.loads(request.content.read())
        params = _getParams(params, APIInfo)

    d = maybeDeferred(func, self, request, params)
    d.addErrback(_handleAPIError, request)

    if APIInfo.get("returnParams"):
        d.addCallback(_verifyReturnParams, APIInfo)

    d.addCallback(_formatResponse, request)

    return d


def _verifyReturnParams(result, APIInfo):

    returnFormat = APIInfo.get("returnFormat", "dict")

    if returnFormat == "dict":

        if isinstance(result, basestring):
            keys = set(json.loads(result).keys())
        else:
            keys = set(result.keys())

        if not isinstance(items, dict):
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
