from models import Menu, Category

__author__ = 'kjydiary'

from mydb import db_session as db

def add_menu(name, price, category_id):
    menu = Menu(name, price, Category.query.filter_by(id=category_id).first())
    db.add(menu)
    db.commit()
    return menu


def modify_menu(id, name, price, category_id):
    new_menu = add_menu(name, price, category_id)
    db.add(new_menu)
    old_menu = Menu.query.filter_by(id=id).first()
    old_menu.available = False
    db.commit()
    return new_menu


def get_all_dict():
    result = []
    for menu in Menu.query.all():
        result.append(menu.convert_dict())
    return result


def get_available_dict():
    result = []
    for menu in Menu.query.all():
        if menu.available:
            result.append(menu.convert_dict())
    return result


def get_one_dict(id):
    return Menu.query.filter_by(id=id).first().convert_dict()