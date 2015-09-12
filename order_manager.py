import sqlalchemy.exc
from models import Order, OrderMenu, Menu

__author__ = 'kjydiary'

from mydb import db_session as db

def add_order(time, totalprice, ordermenus_info):
    order = Order(time, totalprice)

    print("added order", order.convert_dict())

    for ordermenu_info in ordermenus_info:
        menu = Menu.query.filter_by(id=ordermenu_info['id']).first()
        print("before ordermenu create", menu.id, order.id, ordermenu_info['pay'], ordermenu_info['curry'], ordermenu_info['double'])
        ordermenu = OrderMenu(menu=menu, order=order, pay=ordermenu_info['pay'], curry=ordermenu_info['curry'], double=ordermenu_info['double'])
        print("after ordermenu create", ordermenu.id)
        db.add(ordermenu)
        print("after ordermenu add", ordermenu.convert_dict())
    print("end for")
    db.add(order)
    try:
        db.commit()
    except sqlalchemy.exc.IntegrityError as exc:
        reason = exc.message
        print(reason)
    print("end commit")

    return order


def del_order(id):
    order = Order.query.filter_by(id=id).first()
    db.delete(order)
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