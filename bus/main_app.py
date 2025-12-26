import json
import os  # ← добавь импорт

from flask import Flask, render_template,session

from access import login_required
from bp_auth.auth import blueprint_auth
from bp_query.query_route import blueprint_query
from report.route import blueprint_report
from order.route import blueprint_order

app = Flask(__name__, static_folder='../static')
app.secret_key = 'super-secret-key-for-lab'

from database.DBcm import DBContextManager
app.config['db_context'] = DBContextManager

with open('data/db_config.json') as f:
    app.config['db_config'] = json.load(f)

with open('data/access.json') as f:
    app.config['db_access'] = json.load(f)

with open("data/cache_config.json") as f:
    app.config['cache_config'] = json.load(f)

app.register_blueprint(blueprint_query, url_prefix='/query')
app.register_blueprint(blueprint_auth, url_prefix='/auth')
app.register_blueprint(blueprint_report, url_prefix='/report')
app.register_blueprint(blueprint_order, url_prefix='/order')

app.secret_key = 'my secret key'

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/exit')
def system_exit():
    session.clear()
    return render_template('exit.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)