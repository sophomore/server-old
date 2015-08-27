from flask import Flask, request
from models import Menu, Category
from mydb import db_session as db
import mydb

app = Flask(__name__)
app.debug = True


@app.route('/menu/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def one_menu(id):
    menu = Menu.query.filter_by(id=id).first()
    if request.method == 'GET':
        return menu
    elif request.method == 'PUT':
        old_menu = menu
        old_menu.available = False
        new_menu = Menu(request.json['name'], request.json['price'], request.json['category'])
        db.add(new_menu)
        db.commit()
    elif request.method == 'DELETE':
        db.delete(menu)
        db.commit()
    return 'One Menu Info '+id


@app.route('/menu', methods=['GET', 'POST'])
def menu():
    if request.method == 'GET':
        return len(Menu.query.all())
    elif request.method == 'POST':
        menu = Menu(request.form['name'], request.form['price'], request.form['category'])
        db.add(menu)
        db.commit()
    return "Menu Info"


@app.route('/')
def index():
    category = Category("testCateogry1")
    db.add(category)
    db.commit()
    menu = Menu('test1', 8000, category)
    db.add(menu)
    db.commit()
    return "Dear, Song"


@app.route('/db/init')
def initdb():
    mydb.init_db()
    return "init db"


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.remove()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
