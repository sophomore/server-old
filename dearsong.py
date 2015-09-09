from flask import Flask, request, abort
from models import Menu, Category
from mydb import db_session as db
import json
import order_manager
import menu_manager
import statistic

app = Flask(__name__)
app.debug = True

#Menu
@app.route('/menu/<int:id>', methods=['GET', 'PUT'])
def one_menu(id):
    if request.method == 'GET':
        return json.dumps(menu_manager.get_one_dict(id))
    elif request.method == 'PUT':
        new_menu = menu_manager.modify_menu(id, request.form['name'], request.form['price'], request.form['category'])
        return json.dumps({"result":"success", "new_menu": new_menu.convert_dict()})
    return abort(400)


@app.route('/menu', methods=['GET', 'POST'])
def menu():
    if request.method == 'GET':
        return json.dumps(menu_manager.get_available_dict())
    elif request.method == 'POST':
        menu = menu_manager.add_menu(request.form['name'], request.form['price'], request.form['category'])
        return json.dumps({"result":"success", "menu": menu.convert_dict()})
    return abort(400)


@app.route('/menu/all', methods=['GET'])
def menu_all():
    if request.method == 'GET':
        return json.dumps(menu_manager.get_all_dict())
    return abort(400)


#Order
@app.route('/order/<int:id>', methods=['GET', 'DELETE'])
def one_order(id):
    if request.method == 'GET':
        return json.dumps(order_manager.get_one_dict(id))
    elif request.method == 'DELETE':
        order_manager.del_order(id)
        return json.dumps({"result": "success"})
    return abort(400)


@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'GET':
        return json.dumps(order_manager.get_all_dict())
    elif request.method == 'POST':
        order = order_manager.add_order(request.form['time'], request.form['totalprice'], request.form['ordermenus'])
        return json.dumps({"result": "success", "order": order})
    return abort(400)


@app.route('/order/menu/<int:id>', methods=['POST'])
def order_menu_pay(id):
    order_manager.pay(id, request.form['method'])
    return json.dumps({"result", "success"})


@app.route('/statistic')
def statistic_month():
    return json.dumps(statistic.month_money_sum(2014, 7, 2015, 7))


@app.route('/')
def index():
    return "Dear, Song"


@app.route('/db/init')
def initdb():
    import mydb
    mydb.init_db()
    cutlet = Category("돈까스".encode("UTF-8"))
    rice = Category("덮밥".encode("UTF-8"))
    noodle = Category("면류".encode("UTF-8"))
    etc = Category("기타".encode("UTF-8"))
    db.add(cutlet)
    db.add(rice)
    db.add(noodle)
    db.add(etc)
    db.commit()
    return "initialized db"


@app.route('/db/test')
def create_testdata():
    order_manager.add_order('2015-01-10 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-02-10 12:30:20', 16000, [{'id': 3, 'curry': False, 'double': False}])
    order_manager.add_order('2015-03-01 12:30:20', 16000, [{'id': 2, 'curry': False, 'double': False}])
    order_manager.add_order('2015-05-21 12:30:20', 16000, [{'id': 4, 'curry': False, 'double': False}])
    order_manager.add_order('2015-06-24 12:30:20', 16000, [{'id': 1, 'curry': True, 'double': False}])
    order_manager.add_order('2015-07-24 12:30:20', 16000, [{'id': 2, 'curry': False, 'double': False}])
    order_manager.add_order('2015-04-14 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-03-14 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-01-15 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-02-15 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-04-15 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-06-15 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-05-15 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-04-15 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-03-15 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-01-16 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-02-16 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-03-16 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-04-16 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-05-16 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-06-16 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-07-16 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-08-16 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-09-17 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-08-17 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-07-17 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-06-17 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-05-17 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-04-17 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-03-17 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-02-17 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-01-18 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-02-18 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-03-18 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-04-18 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-05-18 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-06-18 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-07-18 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-08-18 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-09-19 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-08-19 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-07-19 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-06-19 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-05-19 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-04-19 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-03-19 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-02-19 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-01-20 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-02-20 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-03-20 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-04-20 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-05-20 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-06-20 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-07-20 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    order_manager.add_order('2015-08-20 12:30:20', 16000, [{'id': 1, 'curry': False, 'double': False}])
    return "create test data"


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.remove()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
