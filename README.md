<p align="center">  
  <a href="https://www.frontegg.com/" rel="noopener" target="_blank">  
    <img style="margin-top:40px" height="50" src="https://frontegg.com/wp-content/uploads/2020/04/logo_frrontegg.svg" alt="Frontegg logo">  
  </a>  
</p>  
<h1 align="center">Frontegg Python SDK</h1>  
  
  
[Frontegg](https://frontegg.com/) is a web platform where SaaS companies can set up their fully managed, scalable and brand aware - SaaS features and integrate them into their SaaS portals in up to 5 lines of code.  
  
  
## Installation  
Frontegg python sdk is available as [pypi package](https://pypi.org/project/frontegg).   
  
Before installing make sure that your app using python 3.  
  
```  
pip install frontegg  
```  
  ## Singing Up To Frontegg
Before you can start with frontegg, please make sure to [sign up](https://portal.frontegg.com/signup) in order to get your free account.

After you signed up, you will be able to get your client ID and API key [here.](https://portal.frontegg.com/administration)
  
  
## Supported Liberies
Frontegg Slack SDK support the following liberies, and more to come:  
  
 - [Flask](frontegg/flask)  
 - [FastAPI](frontegg/fastapi)  
 - [Sanic](frontegg/sanic)  
  
*If you could not find the libary you are looking for here, please [contact us](https://frontegg.com/contact) and let us know :)*  
  
## Debugging  
Frontegg use the python 3 built in [loggin libary](https://docs.python.org/3/library/logging.html) to log useful debugging information.  
  
In order to had those logs you can add the environment variable "FRONTEGG_DEBUG":  
```  
FRONTEGG_DEBUG=True  
``` 
Or configure it in the app itself:  
```  
from frontegg import frontegg_logger  
import logging  
  
frontegg_logger.setLevel(logging.DEBUG)  
```