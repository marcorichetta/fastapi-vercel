from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.config import settings
from app.database.schema.database import Base


def database(connection_string: str):
    db_engine = create_engine(connection_string, echo=True)
    Base.metadata.create_all(db_engine)
    return db_engine


if __name__ == "__main__":
    # Choose which DB you want to connect to
    use_db = input("Choose DB [prod/local]: ").lower()

    if use_db == "prod":
        db_engine = database(settings.DB_URL)
    elif use_db == "local":
        db_engine = database(settings.DB_LOCAL_URL)
    else:
        print("Invalid choice!")


PROD_ENGINE = database(settings.DB_URL)
SessionProd = sessionmaker(autocommit=False, autoflush=False, bind=PROD_ENGINE)
