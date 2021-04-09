from fastapi import FastAPI

from . import account_2 as account
from . import asset_2 as asset


app = FastAPI()


@app.get("/")
async def root():
    return {"pi": "3.1415926535897932384626433"}


app.include_router(account.router)
app.include_router(asset.router)
