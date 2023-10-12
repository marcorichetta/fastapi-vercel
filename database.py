from config import settings
from sqlalchemy import create_engine
from database_models import Base, Product
from sqlalchemy.orm import sessionmaker
from models import AddProductModel, UpdateProductModel
from typing import Union


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


## DB FUNCTIONSfrom models import AddProductModel, UpdateProductModel


def add_product(product_data: AddProductModel) -> int:
    """Add a new product for a user."""
    session = SessionProd()
    try:
        new_product = Product(**product_data)
        session.add(new_product)
        session.commit()
        session.refresh(new_product)
        return new_product
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()


def get_products_by_userid(userid: int):
    """Retrieve all products for a given user."""
    session = SessionProd()
    try:
        products = session.query(Product).filter_by(userid=userid).all()
        return products
    except Exception as e:
        raise
    finally:
        session.close()


def get_product_by_id(product_id: int):
    """Retrieve a product by its primary key."""
    session = SessionProd()
    try:
        product = session.query(Product).get(product_id)
        return product
    except Exception as e:
        raise
    finally:
        session.close()


def get_product_by_url(product_url: str):
    """Retrieve a product by its URL."""
    session = SessionProd()
    try:
        product = session.query(Product).filter_by(url=product_url).first()
        return product
    except Exception as e:
        raise
    finally:
        session.close()


def delete_product_by_id(product_id: int):
    """Delete a product by its primary key."""
    session = SessionProd()
    try:
        product = session.query(Product).get(product_id)
        session.delete(product)
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()


def update_product_by_user_and_url(user_id: int, product_url: str, update_data: Union[dict, UpdateProductModel]):
    """Update a product's details based on user_id and product_url."""
    session = SessionProd()
    try:
        product = session.query(Product).filter_by(userid=user_id, url=product_url).first()
        if not product:
            raise ValueError("No product associated with this user_id and product_url combination.")

        # If update_data is a dictionary, convert it to UpdateProductModel
        if isinstance(update_data, dict):
            update_data = UpdateProductModel(**update_data)

        for key, value in update_data.dict(exclude_unset=True).items():
            setattr(product, key, value)
        session.commit()
        session.refresh(product)
        return product
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()
