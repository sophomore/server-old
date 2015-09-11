from models import Order, OrderMenu, Menu

__author__ = 'kjydiary'

from mydb import db_session as db

def add_order(time, totalprice, ordermenus_info):
    order = Order(time, totalprice)

    for ordermenu_info in ordermenus_info:
        db.add(OrderMenu(Menu.query.filter_by(id=ordermenu_info['id']).first(), order, ordermenu_info['curry'], ordermenu_info['double']))

    db.add(order)
    db.commit()
    return order


def del_order(id):
    order = Order.query.filter_by(id=id).first()
    db.delete(order)
    db.commit()
    #TODO: 주문 정보에 들어있는 OrderMenu 삭제


def pay(id, method):
    ordermenu = OrderMenu.query.filter_by(id=id).first()
    ordermenu.pay = method
    db.commit()


def get_all_dict():
    result = []
    for order in Order.query.all():
        result.append(order.convert_dict())
    return result


def get_one_dict(id):
    return Order.query.filter_by(id=id).first().convert_dict()