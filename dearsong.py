from flask import Flask, request, abort
from models import Menu, Category
from mydb import db_session as db
import json
import order_manager
import menu_manager
import util
import statistic
import os

from datetime import datetime

app = Flask(__name__)
app.debug = True
app.config['UPLOAD_FOLDER'] = '../'


# Menu
@app.route('/menu/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def one_menu(id):
    if request.method == 'GET':
        return json.dumps(menu_manager.get_one_dict(id))
    elif request.method == 'PUT':
        new_menu = menu_manager.modify_menu(id, request.form['name'], request.form['price'], request.form['category'])
        return json.dumps({"result": "success", "new_menu": new_menu.convert_dict()})
    elif request.method == 'DELETE':
        menu = menu_manager.delete_menu(id)
        return json.dumps({"result": "success", "delete_menu": menu.convert_dict()})
        return abort(400)

@app.route('/menu', methods=['GET', 'POST'])
def menu():
    if request.method == 'GET':
        return json.dumps(menu_manager.get_available_dict())
    elif request.method == 'POST':
        menu = menu_manager.add_menu(request.form['name'], request.form['price'], request.form['category'])
        return json.dumps({"result": "success", "menu": menu.convert_dict()})
        return abort(400)

@app.route('/menu/all', methods=['GET'])
def menu_all():
    if request.method == 'GET':
        return json.dumps(menu_manager.get_all_dict())
        return abort(400)

# Order
@app.route('/order/<int:id>', methods=['GET', 'DELETE', 'POST'])
def one_order(id):
    if request.method == 'GET':
        return json.dumps(order_manager.get_one_dict(id))
    elif request.method == 'DELETE':
        order_manager.del_order(id)
        return json.dumps({"result": "success"})
    elif request.method == 'POST':
        return json.dumps(order_manager.get_order(id))

    return abort(400)


@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'GET':
        return json.dumps(order_manager.get_all_dict())
    elif request.method == 'POST':
        order = order_manager.add_order(request.form['time'], request.form['totalprice'],
                                        json.loads(request.form['ordermenus']))
        return json.dumps({"result": "success", "order": order.convert_dict()})
    return abort(400)


@app.route('/order/menu/<int:id>', methods=['POST'])
def order_menu_pay(id):
    order_manager.pay(id, request.form['pay'])
    return json.dumps({"result": "success"})


@app.route('/order/search', methods=['POST'])
def search_order():
    startDate = datetime.strptime(request.form['startDate'], '%Y-%m-%d %H:%M:%S')
    endDate = datetime.strptime(request.form['endDate'], '%Y-%m-%d %H:%M:%S')
    ordermenus = request.form['ordermenus']
    ordermenus = json.loads(ordermenus)
    if len(ordermenus) == 0:
        print('asdf')
        ordermenus2 = Menu.query.all()
        for menu in ordermenus2:
            ordermenus.append(menu.id)
    pay = json.loads(request.form['pay'])
    if len(pay) == 0:
        pay.append(1)
        pay.append(2)
        pay.append(3)
        pay.append(4)
    return json.dumps(order_manager.search(startDate, endDate,ordermenus, pay))

@app.route('/statistic/linechart',methods=['POST'])
def linechart():
    menus = json.loads(request.form['menus'])
    if len(menus) == 0:
        menus2 = []
        menus = db.query(Menu.id).all()
        for menu in menus:
            menus2.append(menu.id)
        return json.dumps(
            statistic.line_chart(request.form['startDate'], request.form['endDate'], menus2, request.form['unit']))
    else:
        return json.dumps(
            statistic.line_chart(request.form['startDate'], request.form['endDate'], request.form['menus'],
                                    request.form['unit']))
@app.route('/statistic/barchart',methods=['POST'])
def barchart():
    menus = json.loads(request.form['menus'])
    if len(menus) == 0:
        menus2 = []
        menus = db.query(Menu.id).all()
        for menu in menus:
            menus2.append(menu.id)
        return json.dumps(
            statistic.bar_chart(request.form['startDate'], request.form['endDate'], menus2, request.form['unit']))
    else:
        return json.dumps(
            statistic.bar_chart(request.form['startDate'], request.form['endDate'], request.form['menus'],
                                    request.form['unit']))

@app.route('/statistic/unit_menu_sum', methods=['POST'])
def statistic_month():
    menus = json.loads(request.form['menus'])
    if len(menus) == 0:
        menus2 = []
        menus = db.query(Menu.id).all()
        for menu in menus:
            menus2.append(menu.id)
        return json.dumps(
            statistic.unit_menu_sum(request.form['startDate'], request.form['endDate'], menus2, request.form['unit']))
    else:
        return json.dumps(
            statistic.unit_menu_sum(request.form['startDate'], request.form['endDate'], request.form['menus'],
                                    request.form['unit']))

@app.route('/order/print/statement', methods=['GET'])
def print_statement():
    o = json.loads(request.form['ordermenus'])
    util.print_statement(o,request.form['time'])

@app.route('/order/<int:id>/print/receipt', methods=['GET'])
def print_receipt():
    return json.dumps({"error":"error"})

@app.route('/file/output', methods=['GET', 'POST'])
def file_mysql():
    if request.method == 'GET':
        util.output()
        return json.dumps({"result": "success"})
    else:
        util.input_two()
        return json.dumps({"result": "success"})


@app.route('/file/input', methods=['POST'])
def file_input():
    file = request.files['file']
    file.save(os.path.join(app.config['UPLOAD_FOLDER'],"backup.xlsx"))
    util.input()
    return json.dumps({"result": "success"})


@app.route('/')
def index():
    return "Dear, Song"


@app.route('/db/init', methods=['PUT'])
def initdb():
    import mydb
    mydb.init_db()
    cutlet = Category("돈까스")
    rice = Category("덮밥")
    noodle = Category("면류")
    etc = Category("기타")
    db.add(cutlet)
    db.add(rice)
    db.add(noodle)
    db.add(etc)
    db.commit()
    return "initialized db"


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.remove()
    if exception:
        print("################################Shutdown DB error#########################################")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)