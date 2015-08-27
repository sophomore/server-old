from flask import Flask, request
from models import Menu, Category
from mydb import db_session as db
import json

app = Flask(__name__)
app.debug = True


@app.route('/menu/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def one_menu(id):
    menu = Menu.query.filter_by(id=id).first()
    if request.method == 'GET':
        menu_json = json.dumps(menu.convert_dict())
        return menu_json
    elif request.method == 'PUT':
        old_menu = menu
        old_menu.available = False
        new_menu = Menu(request.json['name'], request.json['price'], request.json['category'])
        db.add(new_menu)
        db.commit()
        return json.dumps({"result":"success"})
    elif request.method == 'DELETE':
        db.delete(menu)
        db.commit()
        return json.dumps({"result":"success"})
    return abort(400)


@app.route('/menu', methods=['GET', 'POST'])
def menu():
    if request.method == 'GET':
        result = []
        for menu in Menu.query.all():
            result.append(menu.convert_dict())
        return json.dumps(result)
    elif request.method == 'POST':
        menu = Menu(request.form['name'], request.form['price'], request.form['category'])
        db.add(menu)
        db.commit()
        return json.dumps({"result":"success"})
    return abort(400)


@app.route('/')
def index():
    return "Dear, Song"


@app.route('/db/init')
def initdb():
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


@app.route('/db/clear')
def cleardb():
    pass


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.remove()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
