from frontegg.fastapi import frontegg
from frontegg.fastapi.secure_access import FronteggSecurity, User
from fastapi import FastAPI, Depends
import uvicorn

app = FastAPI()


client_id = 'my-client-id'
api_key = 'my-api-key'

frontegg.init_app(app, client_id=client_id, api_key=api_key, with_secure_access=True)


@app.get("/")
def read_root(user: User = Depends(FronteggSecurity())) -> User:
    return user


@app.get("/authorized")
def read_root(user: User = Depends(FronteggSecurity(permissions=['my-permission']))) -> User:
    return user


uvicorn.run(app)
