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
                        APIFunc.__name__ = str("api_v%s_%s" % (version, api["name"]))
                    else:
                        raise Exception("no %s in v%s" % (api["name"], version))

                    if version in processor["versions"]:

                        args = (["/v%s/%s" % (version, processor["endpoint"])],
                            {"methods": api["allowedMethods"]})

                        handler = _make_handler(self.service, APIFunc, args)
                        print "api_v%s_%s" % (version, api["name"])
                        setattr(self.service, "api_v%s_%s" % (version, api["name"]), handler)

        print inspect.getmembers(self.service)

        self.service.app.run("127.0.0.1", 8092)

                    


#from aludel
def _make_handler(service_class, handler_method, arguments):
    args, kw = arguments

    @wraps(handler_method)
    def wrapper(*args, **kw):
        return _handler_wrapper(handler_method, service_class, *args, **kw)
    update_wrapper(wrapper, handler_method)
    route = service_class.app.route(*args, **kw)

    return route(wrapper)

def _handler_wrapper(func, self, request, *args, **kw):
    d = maybeDeferred(func, self, request, *args, **kw)
    #d.addCallback(format_response, request)
    #if hasattr(self, 'handle_api_error'):
    #    d.addErrback(self.handle_api_error, request)
    #d.addErrback(_handle_api_error, request)
    return d