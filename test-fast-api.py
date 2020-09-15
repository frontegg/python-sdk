from frontegg.fastapi import frontegg
from frontegg.fastapi.secure_access import get_user, GetUser, context_provider
from fastapi import FastAPI, Request, Depends, HTTPException
import uvicorn

app = FastAPI()


client_id = '93447df4-edcc-45e5-8664-9fb8c196cf44'
api_key = '71e8ca5a-3786-4d1b-8fcd-a111d07c7bc2'

frontegg.init_app(app, client_id=client_id, api_key=api_key, with_secure_access=True)


@app.get("/")
def read_root(user: GetUser = Depends(get_user)):
    return {"user": user}


uvicorn.run(app)
