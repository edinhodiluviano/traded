import sqlalchemy as sa
from fastapi import FastAPI, Depends

from . import db
from . import account_2 as account
from . import asset_2 as asset
from . import transaction_2 as transaction
from .dependencies import get_session


app = FastAPI()


@app.get("/")
async def root():
    "Try me out. I do no harm (and no good either)"
    return {"pi": "3.1415926535897932384626433"}


@app.get("/db_setup")
def db_setup(session: sa.orm.Session = Depends(get_session)):
    """
    ### test only
    Setups the database tables and some values for testing purpuses.<br>
    This endpoint shreds your database and data when used.
    """
    db.main.setup(session)


app.include_router(account.router)
app.include_router(asset.router)
app.include_router(transaction.router)
