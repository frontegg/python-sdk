<br />
<div align="center">
<img src="https://fronteggstuff.blob.core.windows.net/frongegg-logos/logo-transparent.png" alt="Frontegg Logo" width="400" height="90">

<h3 align="center">Frontegg Python Flask Client</h3>

  <p align="center">
    Frontegg is a web platform where SaaS companies can set up their fully managed, scalable and brand aware - SaaS features and integrate them into their SaaS portals in up to 5 lines of code.
    <br />
    <h3><a href="https://docs.frontegg.com/docs/using-frontegg-sdk"><strong>Explore the docs »</strong></a></h3>
    <a href="https://github.com/frontegg/python-sdk/issues">Report Bug</a>
    ·
    <a href="https://github.com/frontegg/python-sdk/issues">Request Feature</a>
  </p>
</div>
  
# Requirements  

 - [ ] Python 3 installed
 - [ ] Existing app with [flask](https://pypi.org/project/Flask/) installed
 - [ ] [Frontegg library](https://pypi.org/project/frontegg/) installed
 - [ ] Frontegg [Client ID and API key](https://portal.frontegg.com/administration).


# Quick Start

With a few lines of code you will have Frontegg up and running.

Import and initialize Frontegg along with your Flask Application

    from frontegg.flask import frontegg
    from flask import Flask
        
    fe_client_id = 'REPLACE_WITH_FRONTEGG_CLIENT_ID'
    fe_api_key = 'REPLACE_WITH_FRONTEGG_API_KEY'

    frontegg.init_app(fe_client_id, fe_api_key)

    app = Flask('my_first_frontegg_app')
	
	app.run()

Great! Now you have Frontegg up and running. 

# Authentication and Authorization
### Protecting routes
When using Frontegg secure access. You get the ability to protect your routes using Frontegg authentication middleware:

    from flask import g
    from frontegg.flask.secure_access import with_authentication
    
    @app.get("/protected")
    @with_authentication(role_keys=['my-role'], permission_keys=['my-permission'])
	def protected(request):  
	    return g.user

The decorator *with_authentication* get the optional arguments *role_keys* and *permission_keys* to specify which roles and permissions are required in order to access the route.

When using the *with_authentication* decorator, the user data will be set on the request context, as you can see in the example above.

### Access tokens

When using M2M authentication, access tokens will be cached by the SDK.
By default access tokens will be cached locally, however you can use one other kind of cache:

- redis

#### Use redis as your cache
When initializing your context, pass an access tokens options object with your redis parameters

    access_tokens_options = {
      cache: {
        type: 'redis',
        options: {
          host: 'localhost',
          port: 6379,
          password: '',
          db: 10,
        },
      },
    };
    
    frontegg.init_app(fe_client_id, fe_api_key, options)


## CORS (Cross-origin resource sharing)
In order to use Frontegg, it is required that your app will know how to handle CORS.
It's easy to set up:

    from flask_cors import CORS
    
    CORS(app, supports_credentials=True)

## Working with the REST API
Frontegg provides a comprehensive REST API for your application. 
In order to use the API from your backend it is required to initialize the http client using your credentials

    // define your base url
    base_url = "https://api.frontegg.com/audits"
    http_client = HttpClient(client_id=<YOUR_CLIENT_ID>, api_key=<YOUR_API_KEY>, base_url=base_url)

The http client instance can now be used to make API requests to Frontegg's REST API (base on the provided base url)

## Using Frontegg clients
Frontegg provides various clients for seamless integration with the Frontegg API.

For example, Frontegg’s Managed Audit Logs feature allows you to embed an end-to-end working feature in just 5 lines of code

### creating a new Audits client

    from frontegg.common.clients import AuditsClient, HttpClient, Severity

    http_client = HttpClient(client_id=<YOUR_CLIENT_ID>, api_key=<YOUR_API_KEY>, base_url=frontegg_urls.audits_service['base_url'])
    audits_client = AuditsClient(http_client)

## Sending an audit using the newly created client

    audits_client.send_aud
