from flask import Flask
from mydb import db_session

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == '__main__':
    app.run()
