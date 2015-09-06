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

    def convert_dict(self):
        return {"id": self.id, "name": self.name, "menus": self.menus}

    def __init__(self, name):
        self.name = name


class Menu(Base):
    __tablename__ = 'menu'
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    price = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    ordermenus = relationship('OrderMenu')
    available = Column(Boolean, default=True, nullable=False)

    def convert_dict(self):
        return {"id": self.id, "name": self.name, "price": self.price, "category_id": self.category_id,
                "ordermenus": self.ordermenus, "available": self.available}

    def __init__(self, name, price, category, available=True):
        self.name = name
        self.price = price
        self.category_id = category
        category.menus.append(self)
        self.available = available

    def __repr__(self):
        return '<Menu %r>' % self.name


class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    time = Column(DateTime)
    ordermenus = relationship('OrderMenu')
    totalprice = Column(Integer)

    def convert_dict(self):
        return {"id": self.id, "time": self.time, "ordermenus": self.ordermenus, "totalprice": self.totalprice}

    def __init__(self, time, totalprice):
        self.time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        self.totalprice = totalprice


class OrderMenu(Base):
    __tablename__ = 'ordermenu'
    id = Column(Integer, primary_key=True)
    menu_id = Column(Integer, ForeignKey('menu.id'), nullable=False)
    order_id = Column(Integer, ForeignKey('order.id'), nullable=False)
    pay = Column(Integer, nullable=False)

    def convert_dict(self):
        return {"id": self.id, "menu_id": self.menu_id, "order_id": self.order_id, "pay": self.pay}

    def __init__(self, menu, order):
        self.menu_id = menu
        self.order_id = order
        order.ordermenus.append(self)