import sqlalchemy.exc
from models import Order, OrderMenu, Menu

__author__ = 'kjydiary'

from mydb import db_session as db

def add_order(time, totalprice, ordermenus_info):
    order = Order(time, totalprice)

    db.add(order)
    db.commit()

    for ordermenu_info in ordermenus_info:
        ordermenu = OrderMenu(menu=Menu.query.filter_by(id=ordermenu_info['id']).first(), order=order, pay=ordermenu_info['pay'], curry=ordermenu_info['curry'], double=ordermenu_info['double'])
        db.add(ordermenu)

    db.commit()

    return order


def del_order(id):
    order = Order.query.filter_by(id=id).first()
    db.delete(order)
    for ordermenu in order.ordermenus:
        db.delete(ordermenu)
    db.commit()
    #TODO: 주문 정보에 들어있는 OrderMenu 삭제


def pay(id, pay):
    ordermenu = OrderMenu.query.filter_by(id=id).first()
    ordermenu.pay = pay
    db.commit()


def get_all_dict():
    result = []
    for order in Order.query.all():
        result.append(order.convert_dict())
    return result


def get_one_dict(id):
    return Order.query.filter_by(id=id).first().convert_dict()


def search(startDate, endDate, ordermenus, pay):
    print(startDate, endDate, ordermenus, pay)
    orders = []
    for ordermenu in ordermenus:
        orders.append(Order.query.join(Order.ordermenus, aliased=True).filter_by(menu_id=ordermenu, pay=pay).all())

    result =[]
    for order in orders:
        result.append(order.convert_dict())
    return result