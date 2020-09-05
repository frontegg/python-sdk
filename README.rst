.. image:: https://fronteggstuff.blob.core.windows.net/frongegg-logos/logo-transparent.png
   :alt: Frontegg

Frontegg is a web platform where SaaS companies can set up their fully managed, scalable and brand aware - SaaS features and integrate them into their SaaS portals in up to 5 lines of code.

Installation
------------

You can install this library by using pip::

    pip install frontegg

If you'd like to use Frontegg in your flask project use the flask extra dependency::

    pip install frontegg[flask]

Usage
-----

You can directly use the Frontegg REST client to access your data when you need to.
The raw client directly returns a `requests.Response`.

This is useful in Python scripts or in cases where you need to access the data from the server side:

.. code-block:: pycon

    >>> from frontegg import FronteggRESTClient
    >>> client = FronteggRESTClient('your-client-id', 'your-client-secret')
    >>> response = client.request('/metadata', 'GET', params={'entityName': 'audits'})
    >>> print(response.json())
    {'rows': [{'_id': '5d3d2ee54a04a50033da91df', 'entityName': 'audits', 'properties': [
        {'_id': '5d3d2ee54a04a50033da91e6', 'name': 'createdAt', 'displayName': 'Date', 'type': 'Timestamp',
         'filterable': True, 'sortable': True},
        {'_id': '5d3d2ee54a04a50033da91e5', 'name': 'user', 'displayName': 'User', 'type': 'UserIdentity',
         'filterable': True, 'sortable': True},
        {'_id': '5d3d2ee54a04a50033da91e4', 'name': 'resource', 'displayName': 'Resource', 'type': 'AlphaNumeric',
         'filterable': True, 'sortable': True},
        {'_id': '5d3d2ee54a04a50033da91e3', 'name': 'action', 'displayName': 'Action', 'type': 'AlphaNumeric',
         'filterable': True, 'sortable': True}, {
            '_id': '5d3d2ee54a04a50033da91e2', 'name': 'severity', 'displayName': 'Severity', 'type': 'AlphaNumeric',
            'filterable': True, 'sortable': True},
        {'_id': '5d3d2ee54a04a50033da91e1', 'name': 'ip', 'displayName': 'IP Address', 'type': 'AlphaNumeric',
         'filterable': True, 'sortable': True},
        {'_id': '5d3d2ee54a04a50033da91e0', 'name': 'message', 'displayName': 'Message', 'type': 'AlphaNumeric',
         'filterable': True, 'sortable': False}], 'vendorId': 'my-client-id',
                          'id': '39372f0f-1d14-4ecd-8462-1b22d5ca9264', 'createdAt': '2019-07-28T05:13:09.723Z',
                          'updatedAt': '2019-07-28T05:13:09.723Z', '__v': 0}]}

You can pass a context callback to provide the user id and the tenant id that are relevant to the request:

.. code-block:: pycon

    >>> from frontegg import FronteggRESTClient, FronteggContext
    >>> client = FronteggRESTClient('your-client-id', 'your-client-secret', context_callback=lambda request: FronteggContext('user_id@user.com', 'tenant-id'))
    >>> response = client.request('/audits/stats', 'GET')
    >>> print(response.json())
    {'totalToday': 2, 'severeThisWeek': 0}

Higher Level Client
~~~~~~~~~~~~~~~~~~~

You can access the audits API directly using the `FronteggClient`:

.. code-block:: pycon

    >>> from frontegg import FronteggClient
    >>> client = FronteggClient('your-client-id', 'your-client-secret')
    >>> client.send_audits({"username": "test", "severity": "Info"}, tenantId='my-tenant-id')

Proxying Requests From Other Clients
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The browser and possibly other clients in your architecture need to access Frontegg from your proxy
as it determines the context of the request.

This package currently only supports doing so from Flask. In the future, more frameworks may be added.

Flask
+++++

To proxy requests to Frontegg in your Flask application the following configuration must be provided:

.. code-block:: python

    from flask import Flask
    app = Flask('example')
    app.config['FRONTEGG_CLIENT_ID'] = 'your client id'
    app.config['FRONTEGG_API_KEY'] = 'your api key'

You can optionally provide the context callback as a configuration setting as well:

.. code-block:: python

    from frontegg import FronteggContext
    app.config['FRONTEGG_CONTEXT_RESOLVER'] = lambda request: FronteggContext('user_id@user.com', 'my-tenant-id')

The request argument will be filled with the `flask.request` object.
You can use it to determine the user id and the tenant id.

In addition, different users may or may not access specific data and thus have different permissions.
You can use the `frontegg.FronteggPermissions` enum to limit access to your data.

.. code-block:: python

    from frontegg import FronteggContext, FronteggPermissions

    def context_resolver(request):
        if is_admin_user(request):
            permissions = (FronteggPermissions.All,)
        else:
            permissions = (FronteggPermissions.Teams.value.Read,)

        return FronteggContext('user_id@user.com', 'my-tenant-id', permissions=permissions)


To begin proxying requests you should

.. code-block:: python

    from flask import Flask
    from frontegg import FronteggContext
    from frontegg.flask import frotnegg
    app = Flask('example')
    app.config['FRONTEGG_CLIENT_ID'] = 'your client id'
    app.config['FRONTEGG_API_KEY'] = 'your api key'
    app.config['FRONTEGG_CONTEXT_RESOLVER'] = lambda request: FronteggContext('user_id@user.com', 'my-tenant-id')
    frontegg.init_app(app)


aiohttp async support
+++++++++++++++++++++

In case you are using aiohttp as your web infrastructure, Frontegg has support for that as well.
For adding the frontegg middleware to the aiohttp you should

.. code-block:: python

    from aiohttp import web
    from frontegg.aiohttp import Frontegg

    app = web.Application()
    Frontegg(app, 'my-client-id', 'my-api-key', context_resolver)

