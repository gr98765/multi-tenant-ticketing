from .database import Base, engine
from . import models  # noqa: ensures models are registered

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Tables created.")
