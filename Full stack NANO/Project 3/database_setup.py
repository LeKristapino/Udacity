import sys
from sqlalchemy import Column, String, Integer, ForeignKey

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()


class Category(Base):
    __tablename__ = 'categories'
    name = Column(String(100), unique=True, nullable=False)
    id = Column(Integer, primary_key=True)
    items = relationship("Item")

    @property
    def serialize(self):
        items = []
        for item in self.items:
            instance = {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "image": "/uploads/" + item.image
            }
            items.append(instance)
        return {
            'id': self.id,
            'name': self.name,
            'items': items
        }


class Item(Base):
    __tablename__ = 'items'
    name = Column(String(80), nullable=False)
    description = Column(String(500))
    id = Column(Integer, primary_key=True)
    image = Column(String(100))
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship(Category)

engine= create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
