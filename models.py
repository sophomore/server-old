from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy import Column
from sqlalchemy.orm import relationship
from mydb import Base

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    menus = relationship('Menu')

    def __init__(self, name):
        self.name = name


class Menu(Base):
    __tablename__ = 'menu'
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    price = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey('Category.id'), nullable=False)
    ordermenus = relationship('OrderMenu')
    available = Column(Boolean, default=True, nullable=False)

    def __init__(self, name, price, category, available=True):
        self.name = name
        self.price = price
        self.category_id = category
        category.menus.append(self)
        self.available = available


class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    time = Column(DateTime)
    ordermenus = relationship('OrderMenu')

    def __init__(self):
        self.time = datetime.now()


class OrderMenu(Base):
    __tablename__ = 'ordermenu'
    id = Column(Integer, primary_key=True)
    menu_id = Column(Integer, ForeignKey('Menu.id'), nullable=False)
    order_id = Column(Integer, ForeignKey('Order.id'), nullable=False)
    pay = Column(Integer, nullable=False)

    def __init__(self, menu, order):
        self.menu_id = menu
        self.order_id = order
        order.ordermenus.append(self)