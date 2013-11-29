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