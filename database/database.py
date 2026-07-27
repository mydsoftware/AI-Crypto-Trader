"""
PACT-OS Database
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.models import Base


class Database:

    def __init__(self):

        self.engine = create_engine(
            "sqlite:///pact_os.db",
            echo=False,
        )

        Base.metadata.create_all(self.engine)

    def session(self):

        return Session(self.engine)