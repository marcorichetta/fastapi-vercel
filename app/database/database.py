from app.config.config import settings
from contextlib import contextmanager
from sqlalchemy import create_engine
from app.models.database import Base, Product
from sqlalchemy.orm import sessionmaker
from app.models.product import AddProductModel, UpdateProductModel
from typing import Union
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = SessionProd()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()


def add_product(product_data: AddProductModel) -> Product:
    with session_scope() as session:
        try:
            new_product = Product(**product_data)
            session.add(new_product)
            session.commit()
            return new_product
        except Exception as e:
            logger.error(f"Error adding product: {str(e)}")
            raise


def get_products_by_userid(userid: int):
    with session_scope() as session:
        try:
            products = session.query(Product).filter_by(userid=userid).all()
            return products
        except Exception as e:
            logger.error(f"Error retrieving products for userid {userid}: {str(e)}")
            raise


def get_product_by_id(product_id: int):
    with session_scope() as session:
        try:
            product = session.query(Product).get(product_id)
            return product
        except Exception as e:
            logger.error(f"Error retrieving product by id {product_id}: {str(e)}")
            raise


def get_product_by_url(product_url: str):
    with session_scope() as session:
        try:
            product = session.query(Product).filter_by(url=product_url).first()
            if product is None:
                return None

            product_dict = {c.name: getattr(product, c.name) for c in Product.__table__.columns}
            return product_dict  # Return the dict, not the instance
        except Exception as e:
            logger.error(f"Error retrieving product by url {product_url}: {str(e)}")
            raise


def delete_product_by_id(product_id: int):
    with session_scope() as session:
        try:
            product = session.query(Product).get(product_id)
            if product:
                session.delete(product)
            else:
                logger.warning(f"No product found with id {product_id}")
        except Exception as e:
            logger.error(f"Error deleting product with id {product_id}: {str(e)}")
            raise


def update_product_by_user_and_url(user_id: int, product_url: str, update_data: Union[dict, UpdateProductModel]):
    with session_scope() as session:
        try:
            product = session.query(Product).filter_by(userid=user_id, url=product_url).first()
            if not product:
                raise ValueError("No product associated with this user_id and product_url combination.")

            if isinstance(update_data, dict):
                update_data = UpdateProductModel(**update_data)

            for key, value in update_data.dict(exclude_unset=True).items():
                setattr(product, key, value)
            session.refresh(product)
            return product
        except Exception as e:
            logger.error(f"Error updating product for user_id {user_id} and url {product_url}: {str(e)}")
            raise
