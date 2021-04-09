from . import db


def get_session():
    session = db.main.SessionLocal()
    try:
        yield session
    finally:
        session.close()
