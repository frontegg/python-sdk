<p align="center">  
  <a href="https://www.frontegg.com/" rel="noopener" target="_blank">  
    <img style="margin-top:40px" height="50" src="https://frontegg.com/wp-content/uploads/2020/04/logo_frrontegg.svg" alt="Frontegg logo">  
  </a>  
</p>  
<h1 align="center">Frontegg Python SDK -Flask</h1>  
  
  
[Frontegg](https://frontegg.com/) is a web platform where SaaS companies can set up their fully managed, scalable and brand aware - SaaS features and integrate them into their SaaS portals in up to 5 lines of code.  
  
  
# Requirements  

 - [ ] Python 3 installed
 - [ ] Existing app with [flask](https://pypi.org/project/Flask/) installed
 - [ ] [Frontegg libary](https://pypi.org/project/frontegg/) installed
 - [ ] Fonrtegg [Client ID and API key](https://portal.frontegg.com/administration).


# Quick Start

With a few lines of code you can have frontegg up and running

First make sure that you have a flask app

    from flask import Flask
    app = Flask('my_first_frontegg_app')
	
	app.run()

And then just add frontegg

    from frontegg.flask.secure_access import context_provider
    from frontegg.flask import frontegg
        
    fe_client_id = 'my_frontegg_client_id'
    fe_api_key = 'my_frontegg_api_key'
    frontegg.init_app(app, fe_client_id, fe_api_key, context_provider)
    
Great! Now you have frontegg up and running. 

# Authentication and Authorization
In order to let frontegg know who is the client that make each request and if it's authroize frontegg will need you to provide additional data.

## Using Secure Access
If you are using [frontegg secure access](https://frontegg.com/secure-access-experience) you can just set the flag "*with_secure_access*" and we will handle the authorization and the authentication for you.

    frontegg.init_app(app, fe_client_id, fe_api_key, with_secure_access=True)

### Using frontegg permissions
by deafult frontegg provide a set of permissions for all of it's endpoints , after you assigned those permissions to your roles. you will be able to set them by setting the prtmissions context provider:

    
    from frontegg.flask.secure import context_provider_with_permissions as context_provider
    
    frontegg.init_app(app, fe_client_id, fe_api_key,context_provider, with_secure_access=True)

## Authentication middleware
> If you are using frontegg secure access you can skip this part

In case you are not using frontegg secure access, you will have to authorize the user by yourself.
for each request that is not a public request frontegg will call a fucntion that you will provide.
 
### For example:

    from flask import abort
    
    def auth_middleware(request):
	    if request.is_authenticated:
		    return
		else:
			abort(401)


## Context Provider

> If you are using frontegg secure access you can skip this part

For the authorization part, for each request, frontegg will need to know by which user and on behalf of what tenant the request was made.

You can do this passing "context_provider" function to frontegg.
### For example: 

    from frontegg import FronteggContext
    
    def context_provider(request):
	    if request.user:
		    return FronteggContext(request.user.id, request.user.tenant_id)
	
