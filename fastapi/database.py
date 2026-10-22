import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:devpassword@localhost:5432/alertsdb",
)
engine = create_engine(DATABASE_URL)


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
