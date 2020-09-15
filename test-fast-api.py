from frontegg.fastapi import frontegg
from frontegg.fastapi.secure_access import get_user, GetUser, context_provider
from fastapi import FastAPI, Request, Depends, HTTPException
import uvicorn

app = FastAPI()


client_id = 'my-client-id'
api_key = 'my-api-key'

frontegg.init_app(app, client_id=client_id, api_key=api_key, with_secure_access=True)


@app.get("/")
def read_root(user: GetUser = Depends(get_user)):
    return {"user": user}


uvicorn.run(app)
