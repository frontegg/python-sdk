<p align="center">  
  <a href="https://www.frontegg.com/" rel="noopener" target="_blank">  
    <img style="margin-top:40px" height="50" src="https://frontegg.com/wp-content/uploads/2020/04/logo_frrontegg.svg" alt="Frontegg logo">  
  </a>  
</p>  
<h1 align="center">Frontegg Python SDK - FastAPI</h1>  
  
  
[Frontegg](https://frontegg.com/) is a web platform where SaaS companies can set up their fully managed, scalable and brand aware - SaaS features and integrate them into their SaaS portals in up to 5 lines of code.  
  
  
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
    
    frontegg.init_app(app, fe_client_id, fe_api_key, context_provider)
    
Great! Now you have frontegg up and running. 

# Authentication and Authorization
In order to let Frontegg know who is the client that make each request and if it is authorized Frontegg will need you to provide additional data.

## Using Secure Access
If you are using [frontegg secure access](https://frontegg.com/secure-access-experience) you can just set the flag "*with_secure_access*" and we will handle the authorization and the authentication for you.

    frontegg.init_app(app, fe_client_id, fe_api_key, with_secure_access=True)

### Using frontegg permissions
By default Frontegg provides a set of permissions for all of it's endpoints , after you assigned those permissions to your roles using [Frontegg portal](https://portal.frontegg.com/secure/rolesandpermissions/roles). You will be able to enforce them by setting the permissions context provider:

    
    from frontegg.fastapi.secure import context_provider_with_permissions as context_provider
    
    frontegg.init_app(app, fe_client_id, fe_api_key, context_provider, with_secure_access=True)

### Protecting routes
When using Frontegg secure access. You get the ability to protect your routes using Frontegg authentication middleware:

    from frontegg.fastapi.secure_access import FronteggSecurity, User
    
    @app.get("/protected")  
	def protected(user: User = Depends(FronteggSecurity(permissions=['my-permission']))) -> User:  
	    return user

The function FronteggSecurity get the optional argument *permission_keys* to specify which permissions are required in order to access the route.

## Authentication middleware
> If you are using frontegg secure access you can skip this part

In case you are not using Frontegg secure access, you will have to provide authentication middleware by yourself.
For each request that is not a public request Frontegg will call this authentication middleware, here is an example:
 
    from fastapi import HTTPException
    
    def auth_middleware(request):
	    if request.is_authenticated:
		    return
		else:
		    raise HTTPException(status_code=401,  detail="Unauthenticated")


## Context Provider

> If you are using frontegg secure access you can skip this part

For the authorization part, Frontegg will need to know by which user and on behalf of what tenant the request was made.

You can handle it by passing *context_provider* function to Frontegg. For example:

    from frontegg import FronteggContext
    
    def context_provider(request):
	    if request.user:
		    return FronteggContext(request.user.id, request.user.tenant_id)
		    

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
