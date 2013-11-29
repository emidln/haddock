The Haddock API Description Language
====================================

The API Description Language ends up having two parts - the `metadata` and the `api`. They are laid out like this:

~~~~{json}
{
	"metadata": {
		...
	},
	"api": {
		...
	}
}
~~~~

Metadata
--------

The `metadata` contains three things:

- `name`: The computer-friendly name.
- `friendlyName`: The user-friendly name.
- `versions`: A list of applicable versions. They don't have to be 1, 2, or whatever - they're just used later on in `api`.

API
---

The `api` contains a list of dicts, which are API endpoints. In each API method there is:

- `name`: The computer-friendly name. This is used in naming your functions later!
- `friendlyName`: The user-friendly name.
- `description`: The user-friendly description.
- `allowedMethods`: What HTTP methods are allowed as a part of this endpoint. I'd recommend making different endpoints for `GET`, `PUT`, etc.
- `processors`: A list of dicts, which will be entered into below.

Processors
----------

Processors are the backbone of your API - they are the things behind the endpoints. They contain the following fields in the dict:

- `versions`: A list of versions (see `metadata`) which this endpoint applies to.
- `endpoint`: The HTTP endpoint where it will sit. This is after the version parameter in the URI - so putting in "weather" on v1 will end up with `/v1/weather`.
- `paramsType` (optional): Where the params will be - either `url` (in `request.args`) or `jsonbody` (for example, the body of a HTTP POST). Defaults to `url`.
- `optionalParams` (optional): JSON keys that the API consumer can give, if they want to.
- `requiredParams` (optional): JSON keys that the API consumer *has* to give.
- `returnParams` (optional): dict keys that your API *has* to return.
- `optionalReturnParams` (optional): dict keys that your API may return.

Please note that if you have set `requiredParams`, you MUST set every other key that may be given in `optionalParams`! Same goes with `returnParams`.


All Together
------------

All together, you get something like this...

~~~~{json}
{
    "metadata": {
        "name": "APIExample",
        "friendlyName": "HawkOwl's API Example",
        "versions": [1, 2]
    },
    "api": [
        {
            "name": "getWeather",
            "friendlyName": "Get Weather",
            "description": "Gets the weather.",
            "allowedMethods": ["GET"],
            "processors": [
                {   
                    "versions": [1],
                    "endpoint": "weather",
                    "paramsType": "url",
                    "optionalParams": ["countryCode"],
                    "requiredParams": ["postcode", "unixTimestamp"]
                },
                {
                    "versions": [2],
                    "endpoint": "weather",
                    "paramsType": "url",
                    "requiredParams": ["postcode", "countryCode", "unixTimestamp"],
                    "returnParams": ["temperature", "windSpeed", "isRaining"]
                }
            ]
        }
    ]
}

~~~~