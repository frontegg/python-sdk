import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from frontegg.fastapi import frontegg
from frontegg.fastapi.secure_access import FronteggSecurity, User

app = FastAPI()
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
client_id = 'my-client-id'
api_key = 'my-api-key'

# options = {
#     "access_tokens_options": {
#         "cache": {
#             "type": "redis",
#             "options": {
#                 "host": "localhost",
#                 "port": 6379,
#                 "password": "",
#                 "db": 10,
#             },
#         },
#     }
# }


@app.get("/")
def read_root(user: User = Depends(FronteggSecurity())) -> User:
    return user


@app.get("/authorized")
def read_root(user: User = Depends(FronteggSecurity(permissions=['my-permission']))) -> User:
    return user


async def startup_event():
    await frontegg.init_app(client_id=client_id, api_key=api_key)


app.add_event_handler("startup", startup_event)

uvicorn.run(app, port=8080)
