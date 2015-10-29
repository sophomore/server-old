from models import Order, OrderMenu, Menu

__author__ = 'kjydiary'

from mydb import db_session as db

def add_order(time, totalprice, ordermenus_info):
    order = Order(time, totalprice)
    db.add(order)
    db.commit()

    for ordermenu_info in ordermenus_info:
        menu =  Menu.query.filter_by(id=ordermenu_info['menu_id']).first()
        print(menu)
        ordermenu = OrderMenu(menu=menu, order=order, pay=ordermenu_info['pay'], curry=ordermenu_info['curry'], twice=ordermenu_info['twice'],takeout=ordermenu_info['takeout'])
        db.add(ordermenu)

    db.commit()

    return order


def del_order(id):
    order = Order.query.filter_by(id=id).first()
    if not order== None:
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
    for order in Order.query.order_by(Order.id.desc()).all():
        result.append(order.convert_dict())
    return result


def get_one_dict(id):
    return Order.query.filter_by(id=id).first().convert_dict()


def search(startDate, endDate, ordermenus, pays):
    orders = []
    db_order = Order.query.filter_by(startDate<=Order.time, Order.time<=endDate).order_by(Order.time.desc()).all()
    for order in db_order:
        for j in order.ordermenus:
            if j.pay in pays:
                orders += order
                break;
    result =[]
    for order in orders:
        result.append(order.convert_dict())
    return result

def get_order(id):
    result = []
    orders = db.query(Order).filter(Order.id<id).order_by(Order.id.desc()).limit(10).all()
    for order in orders:
        result.append(order.convert_dict())
    return result