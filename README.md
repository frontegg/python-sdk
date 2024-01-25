<br />
<div align="center">
<img src="https://fronteggstuff.blob.core.windows.net/frongegg-logos/logo-transparent.png" alt="Frontegg Logo" width="400" height="90">

<h3 align="center">Frontegg Python Client</h3>

  <p align="center">
    Frontegg is a web platform where SaaS companies can set up their fully managed, scalable and brand aware - SaaS features and integrate them into their SaaS portals in up to 5 lines of code.
    <br />
    <h3><a href="https://docs.frontegg.com/docs/using-frontegg-sdk"><strong>Explore the docs »</strong></a></h3>
    <a href="https://github.com/frontegg/python-sdk/issues">Report Bug</a>
    ·
    <a href="https://github.com/frontegg/python-sdk/issues">Request Feature</a>
  </p>
</div>

<h3>Table of Contents</h3>
<ul>
    <li><a href="#breaking-changes">Breaking Changes</a></li>
    <li><a href="#installation">Installation</a></li>
    <li><a href="#usage">Usage</a></li>
</ul>

<br/>

## Breaking Changes

* ### As of version 2.0.0 , we will no longer provide proxy middlewares.
* ### As of version 3.0.0, Python 3.7 is no longer supported.

---

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
Frontegg Slack SDK support the following frameworks: 
  
 - [Flask](frontegg/flask)  
 - [FastAPI](frontegg/fastapi)  
  
*If you could not find the library you are looking for here, please [contact us](https://frontegg.com/contact) and let us know :)*  
  
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
