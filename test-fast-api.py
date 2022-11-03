from frontegg.fastapi import frontegg
from frontegg.fastapi.secure_access import FronteggSecurity, User, context_provider_with_permissions
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

client_id = 'my-client-id'
api_key = 'my-api-key'

frontegg.init_app(client_id=client_id, api_key=api_key)

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

@app.get("/")
def read_root(user: User = Depends(FronteggSecurity())) -> User:
    return user


@app.get("/authorized")
def read_root(user: User = Depends(FronteggSecurity(permissions=['my-permission']))) -> User:
    return user


uvicorn.run(app, port=8080)
