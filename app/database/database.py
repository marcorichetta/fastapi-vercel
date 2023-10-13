import logging
from typing import Union
from contextlib import contextmanager

from app.database.schema.database import Product
from app.models.product import AddProductModel, UpdateProductModel
from app.database.db_setup import SessionProd


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
            new_product = Product(**product_data.dict())
            session.add(new_product)
            return new_product
        except Exception as e:
            logger.error(f"Error adding product: {str(e)}")
            raise ValueError("Could not add product. Check the logs for more information.")


def get_products_by_userid(userid: int):
    if not isinstance(userid, int):
        raise ValueError("User ID must be an integer.")

    with session_scope() as session:
        try:
            products = session.query(Product).filter_by(userid=userid).all()
            if not products:
                logger.warning(f"No products found for userid {userid}")
                return []
            return products
        except Exception as e:
            logger.error(f"Error retrieving products for userid {userid}: {str(e)}")
            raise ValueError("Could not retrieve products. Check the logs for more information.")


def get_product_by_id(product_id: int):
    if not isinstance(product_id, int):
        raise ValueError("Product ID must be an integer.")

    with session_scope() as session:
        try:
            product = session.query(Product).get(product_id)
            if not product:
                logger.warning(f"No product found with id {product_id}")
                return None
            return product
        except Exception as e:
            logger.error(f"Error retrieving product by id {product_id}: {str(e)}")
            raise ValueError("Could not retrieve product. Check the logs for more information.")


def get_product_by_url(product_url: str):
    with session_scope() as session:
        try:
            product = session.query(Product).filter_by(url=product_url).first()
            if product is None:
                logger.warning(f"No product found with url {product_url}")
                return None
            product_dict = {c.name: getattr(product, c.name) for c in Product.__table__.columns}
            return product_dict
        except Exception as e:
            logger.error(f"Error retrieving product by url {product_url}: {str(e)}")
            raise ValueError("Could not retrieve product. Check the logs for more information.")


def delete_product_by_id(product_id: int):
    if not isinstance(product_id, int):
        raise ValueError("Product ID must be an integer.")

    with session_scope() as session:
        try:
            product = session.query(Product).get(product_id)
            if product:
                session.delete(product)
                session.commit()
            else:
                logger.warning(f"No product found with id {product_id}")
        except Exception as e:
            logger.error(f"Error deleting product with id {product_id}: {str(e)}")
            raise ValueError("Could not delete product. Check the logs for more information.")


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
            raise ValueError("Could not update product. Check the logs for more information.")
