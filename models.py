from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, Numeric, MetaData, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

def get_or_create(session, model, **kwargs):
    '''Wrapper function for INSERT if not exists'''
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance

# Model declarations for the various tables:
class Brand(Base):
    __tablename__ = 'brands'
    id   = Column(Integer, primary_key=True)
    name = Column(String)

    products = relationship('Product', back_populates='brands')

class Category(Base):
    __tablename__ = 'categories'
    id        = Column(Integer, primary_key=True)
    name      = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    
    children  = relationship('Category')
    products  = relationship('Product', back_populates='categories')

class Store(Base):
    __tablename__ = 'stores'
    id   = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    products = relationship('Product', back_populates='stores')

class Product(Base):
    __tablename__ = 'products'
    id            = Column(Integer, primary_key=True)
    name          = Column(String, nullable=False)
    type          = Column(String)
    price         = Column(Numeric(12,2), nullable=False)
    page_position = Column(Integer, nullable=False)
    page_number   = Column(Integer, nullable=False)
    category_id   = Column(Integer, ForeignKey('categories.id'))
    brand_id      = Column(Integer, ForeignKey('brands.id'))
    store_id      = Column(Integer, ForeignKey('stores.id'))

    brands = relationship('Brand', back_populates='products')
    categories = relationship('Category', back_populates='products')
    stores = relationship('Store', back_populates='products')