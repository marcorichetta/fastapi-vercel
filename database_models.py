from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    userid = Column(String(100), primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255), unique=True)
    phone_number = Column(String(15), unique=True)
    countries_allowed = Column(Integer)
    country_list = Column(JSON, nullable=True)  # Using JSON type for country_list


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    userid = Column(String(100))
    url = Column(String(191))
    title = Column(String(255))

    # Fields from ScrapedData
    scrape_details = Column(String(5000), nullable=True)
    analysis_result = Column(String(5000), nullable=True)
    country_pricing_analysis = Column(JSON, nullable=True)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
