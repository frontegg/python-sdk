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
    <li><a href="#security">Security</a></li>
</ul>

<br/>

## Breaking Changes

* ### As of version 2.0.0 , we will no longer provide proxy middlewares.
* ### As of version 3.0.0, Python 3.7 is no longer supported.
* ### As of version 4.0.0, Python 3.8 and 3.9 are no longer supported and Python 3.10+ is required.

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
  
## Fetching audit logs (v2)

```python
from frontegg.common.clients import AuditsClient, HttpClient
from frontegg.helpers.frontegg_urls import frontegg_urls

http = HttpClient(client_id, api_key, frontegg_urls.audits_service['base_url'])
audits = AuditsClient(http)
page = audits.get_audits_v2(
    tenant_id="tenant-id", count=200, offset=0,
    created_from="2026-11-01T00:00:00Z",
    users=["user-id"], email=["user@example.com"],
    sort_by="createdAt", sort_direction="desc",
)
```

Use your configured client ID and API key for `client_id` and `api_key`.
Request each page with `count` between 1 and 200 and a nonnegative `offset`.
Date filters accept ISO 8601 strings; `tenant_ids`, `users`, and `email` accept
lists. The method returns the API response JSON unchanged and propagates HTTP
errors. It uses the existing vendor authentication and configured audits URL.

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

## <a name="security"></a>Security

The `frontegg` Python SDK is actively maintained, and its dependencies are kept on current, patched versions. Minimum versions of security-sensitive dependencies (`requests`, `cryptography`, `aiohttp`, `PyJWT`, ...) are pinned in `pyproject.toml` so that installs resolve to patched releases.

To keep your application protected, always use the latest release:

```
pip install --upgrade frontegg
```

### Reporting a vulnerability

If you discover a security vulnerability in this SDK, please report it responsibly by emailing **security@frontegg.com**. Please do not open a public GitHub issue for security reports.
