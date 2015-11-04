import json
from models import Order, OrderMenu, Menu
import util

__author__ = 'kjydiary'

from mydb import db_session as db

def add_order(time, totalprice, ordermenus_info):
    order = Order(time, totalprice)
    db.add(order)
    db.commit()

    for ordermenu_info in ordermenus_info:
        menu =  Menu.query.filter_by(id=ordermenu_info['menu_id']).first()
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


def search(startDate, endDate, menus, pays):
    orders = []

    db_order = Order.query.filter(startDate<=Order.time, Order.time<=endDate).order_by(Order.time.desc()).all()
    if len(menus) == 0:
        result = []
        for order in db_order:
            result.append(order.convert_dict())
        return result

    if len(pays) == 0:
        pays = []
        pays.append(1)
        pays.append(2)
        pays.append(3)
        pays.append(4)
    for order in db_order:
        count = 0
        for ordermenu in order.ordermenus:
            if ordermenu.menu_id in menus and ordermenu.pay in pays:
                count+=1
        if count == len(menus):
            orders.append(order)
    result =[]
    for order in orders:
        result.append(order.convert_dict())
    return result

def get_order(time):
    result = []
    orders = db.query(Order).filter(Order.time<time).order_by(Order.time.desc()).limit(20).all()
    print(orders)
    for order in orders:
        result.append(order.convert_dict())
    return result