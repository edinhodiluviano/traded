from fastapi import FastAPI

from . import account_2 as account


app = FastAPI()


@app.get("/")
async def root():
    return {"pi": "3.1415926535897932384626433"}


app.include_router(account.router)
