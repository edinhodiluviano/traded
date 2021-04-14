from fastapi import Depends

from . import db


@Depends
def sess():
    session = db.main.SessionLocal()
    try:
        yield session
    finally:
        session.close()
