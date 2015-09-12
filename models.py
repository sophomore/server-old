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
        self.name = str(name).encode("UTF-8")


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
        self.name = str(name).encode("UTF-8")
        self.price = price
        self.category_id = category
        category.menus.append(self)
        self.available = available

    def __repr__(self):
        return '<Menu %r>' % self.name


class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    time = Column(DateTime, nullable=False)
    ordermenus = relationship('OrderMenu')
    totalprice = Column(Integer, nullable=False)
    takeout = Column(Boolean, default=False, nullable=False)

    def convert_dict(self):
        return {"id": self.id, "time": self.time.strftime("%Y-%m-%d %H:%M:%S"), "ordermenus": self.ordermenus, "totalprice": self.totalprice, "takeout": self.takeout}

    def __init__(self, time, totalprice):
        self.time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        self.totalprice = totalprice
        self.takeout = False


class OrderMenu(Base):
    __tablename__ = 'ordermenu'
    id = Column(Integer, primary_key=True)
    menu_id = Column(Integer, ForeignKey('menu.id'), nullable=False)
    order_id = Column(Integer, ForeignKey('order.id'), nullable=False)
    pay = Column(Integer, nullable=False)
    curry = Column(Boolean, default=False, nullable=False)
    double = Column(Boolean, default=False, nullable=False)
    totalprice = Column(Integer, nullable=False)

    def convert_dict(self):
        return {"id": self.id, "menu_id": self.menu_id, "order_id": self.order_id, "pay": self.pay, "curry": self.curry, "double": self.double, "totalprice": self.totalprice}

    def __init__(self, menu, order, curry=False, double=False):
        self.menu_id = menu
        self.order_id = order
        self.curry = curry
        self.double = double
        self.totalprice = menu.price
        if curry:
            self.totalprice += 1000
        if double:
            self.totalprice += 500
        #TODO: 가격 확인
        # order.ordermenus.append(self)