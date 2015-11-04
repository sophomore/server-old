import json
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

from flask import Flask, request, abort

from models import Category, Order
from mydb import db_session as db
import order_manager
import menu_manager
import util
import statistic

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
        if request.form['price'] !=None and request.form['name']!= None and request.form['category'] != None:
            menu = menu_manager.add_menu(request.form['name'], request.form['price'], request.form['category'])
        else:
            return json.dumps({"result" : "input error"})
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

@app.route('/order', methods=['GET', 'POST','PUT'])
def order():
    if request.method == 'GET':
        return json.dumps(order_manager.get_order())
    elif request.method == 'POST':
        order = order_manager.add_order(request.form['time'], request.form['totalprice'],
                                        json.loads(request.form['ordermenus']))
        return json.dumps({"result": "success", "order": order.convert_dict()})
    elif request.method == 'PUT':
        if request.form['lastDate'] == None:
            return abort(400)
        else:
            date = request.form['lastDate']
            date = datetime.strptime(date,'%Y-%m-%d %H:%M:%S')
        return json.dumps(order_manager.get_order(date))

    return abort(400)


@app.route('/order/menu/<int:id>', methods=['POST'])
def order_menu_pay(id):
    order_manager.pay(id, request.form['pay'])
    return json.dumps({"result": "success"})


@app.route('/order/search', methods=['POST'])
def search_order():
    startDate = datetime.strptime(request.form['startDate']+" 00:00:00", '%Y-%m-%d %H:%M:%S')
    endDate = datetime.strptime(request.form['endDate']+" 23:59:59", '%Y-%m-%d %H:%M:%S')
    menus = request.form['menus']
    menus = json.loads(menus)
    pay = json.loads(request.form['pay'])
    return json.dumps(order_manager.search(startDate, endDate,menus, pay))

@app.route('/today',methods=['GET'])
def get_price_today():
    if request.method == 'GET':
        return json.dumps(order_manager.get_price_today())

#statistic
@app.route('/statistic/linechart',methods=['POST'])
def linechart():
    menus = json.loads(request.form['menus'])
    if len(menus) == 0:
        menus2 = util.get_menus()
        for menu in menus2:
            menus.append(menu)
        return json.dumps(
            statistic.line_chart(request.form['startDate'], request.form['endDate'], menus, request.form['unit']))
    else:
        return json.dumps(
            statistic.line_chart(request.form['startDate'], request.form['endDate'], menus,
                                    request.form['unit']))

@app.route('/statistic/barchart',methods=['POST'])
def barchart():
    menus = json.loads(request.form['menus'])
    if len(menus) == 0:
        menus2 = []
        menus = util.get_menus()
        for menu in menus:
            menus2.append(menu)
        return json.dumps(
            statistic.bar_chart(request.form['startDate'], request.form['endDate'], menus2, request.form['unit']))
    else:
        return json.dumps(
            statistic.bar_chart(request.form['startDate'], request.form['endDate'], request.form['menus'],
                                    request.form['unit']))

@app.route('/order/<int:id>/print/receipt', methods=['GET'])
def print_statement(id):
    order = db.query(Order).filter(Order.id == id).first()
    if order == None:
        return json.dumps({"result": "error", "error":"Not found order id"+str(id)})
    else:
        util.print_receipt(order)
        return json.dumps({"result":"success"})

@app.route('/order/<int:id>/print/statement', methods=['GET'])
def print_receipt(id):
    order = db.query(Order).filter(Order.id == id).first()
    time = order.time
    ordermenus = order.ordermenus
    if order ==  None:
        return json.dumps({"result":"error","error":"Not found order id"+str(id)})
    else:
        util.print_statement(ordermenus,time)
        return json.dumps({"result":"success"})

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

@app.errorhandler(500)
def internal_error(exception):
    app.logger.error(exception)
    abort(500)

@app.teardown_appcontext

def shutdown_session(exception=None):
    db.remove()
    if exception:
        print("################################Shutdown DB error#########################################")


if __name__ == '__main__':
    import logging
    logging.basicConfig(filename='/home/song/error.log',level=logging.DEBUG, backupCount=20)
    app.run(host='0.0.0.0', port=80)