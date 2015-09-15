from flask import Flask, request, abort
from models import Menu, Category
from mydb import db_session as db
import json
import order_manager
import menu_manager
import statistic
from datetime import datetime

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
        order = order_manager.add_order(request.form['time'], request.form['totalprice'], json.loads(request.form['ordermenus']))
        return json.dumps({"result": "success", "order": order.convert_dict()})
    return abort(400)


@app.route('/order/menu/<int:id>', methods=['POST'])
def order_menu_pay(id):
    order_manager.pay(id, request.form['pay'])
    return json.dumps({"result", "success"})


@app.route('/order/search', methods=['POST'])
def search_order():
    startDate = datetime.strptime(request.form['startDate'], '%Y-%m-%d %H:%M:%S')
    print(startDate)
    print(datetime.strptime(request.form['startDate'], '%Y-%m-%d %H:%M:%S'))
    endDate = datetime.strptime(request.form['endDate'], '%Y-%m-%d %H:%M:%S')
    return json.dumps(order_manager.search(startDate, endDate, request.form['ordermenus'], request.form['pay']))


@app.route('/statistic/<int:startYear>/<int:startMonth>/<int:endYear>/<int:endMonth>', methods=['GET'])
def statistic_month(startYear, startMonth, endYear, endMonth):
    return json.dumps(statistic.month_money_sum(startYear, startMonth, endYear, endMonth))

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
