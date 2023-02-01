<br />
<div align="center">
<img src="https://fronteggstuff.blob.core.windows.net/frongegg-logos/logo-transparent.png" alt="Frontegg Logo" width="400" height="90">

<h3 align="center">Frontegg Node.js Client</h3>

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

First make sure that you have a fastAPI app

    from fastapi import FastAPI
    import uvicorn
    
    app = FastAPI()
	
	uvicorn.run(app)

And then just add frontegg

    from frontegg.fastapi import frontegg
    from frontegg.fastapi.secure_access import context_provider

    fe_client_id = 'REPLACE_WITH_FRONTEGG_CLIENT_ID'
    fe_api_key = 'REPLACE_WITH_FRONTEGG_API_KEY'
    
    frontegg.init_app(fe_client_id, fe_api_key)
    
Great! Now you have frontegg up and running. 

# Authentication and Authorization
In order to let Frontegg know who is the client that make each request and if it is authorized Frontegg will need you to provide additional data.

## Using Secure Access
If you are using [frontegg secure access](https://frontegg.com/secure-access-experience) you can just set the flag "*with_secure_access*" and we will handle the authorization and the authentication for you.

    frontegg.init_app(fe_client_id, fe_api_key)

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
