<br />
<div align="center">
<img src="https://fronteggstuff.blob.core.windows.net/frongegg-logos/logo-transparent.png" alt="Frontegg Logo" width="400" height="90">

<h3 align="center">Frontegg Python FastAPI Client</h3>

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
 - [ ] Existing app with [fastAPI](https://fastapi.tiangolo.com/) installed
 - [ ] [Frontegg library](https://pypi.org/project/frontegg/) installed
 - [ ] Frontegg [Client ID and API key](https://portal.frontegg.com/administration).


# Quick Start

With a few lines of code you can have frontegg up and running

Import and initialize Frontegg along with your FastApi Application

    from frontegg.fastapi import frontegg
    from fastapi import FastAPI
    import uvicorn

    fe_client_id = 'REPLACE_WITH_FRONTEGG_CLIENT_ID'
    fe_api_key = 'REPLACE_WITH_FRONTEGG_API_KEY'
    
    frontegg.init_app(fe_client_id, fe_api_key)

    app = FastAPI()
	uvicorn.run(app)

Great! Now you have frontegg up and running. 

# Authentication and Authorization

### Protecting routes
When using Frontegg secure access. You get the ability to protect your routes using Frontegg authentication middleware:

    from frontegg.fastapi.secure_access import FronteggSecurity, User
    
    @app.get("/protected")  
	def protected(user: User = Depends(FronteggSecurity(permissions=['my-permission']))) -> User:  
	    return user

The function FronteggSecurity get the optional argument *permission_keys* to specify which permissions are required in order to access the route.

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

    from fastapi.middleware.cors import CORSMiddleware
    
    origins = [
        "http://localhost:3000",
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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

    audits_client.send_audit(audit={'severity': Severity.INFO}, tenant_id="tenant-id")