# Gevent needed for sockets
from gevent import monkey
monkey.patch_all()

# Imports
import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
import pandas as pd
import ast

# Configure app
socketio = SocketIO()
app = Flask(__name__)
app.config.from_object(os.environ["APP_SETTINGS"])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# DB
db = SQLAlchemy(app)

# Data setup
file_path = "./dataGeneration/problemData.csv"
leetcode_data = pd.read_csv(file_path)
NON_HINT_TAGS = {'array', 'string', 'math', 'tree', 'graph', 'design', 'brainteaser', 'linked-list', 'geometry', 'random'}
titleToTags = {}
titleToURL = {}

for index, d in leetcode_data.iterrows():
  titleToTags[d['title']] = ast.literal_eval(d['tags'])
  titleToURL[d['title']] = d['url']

# Import + Register Blueprints
from app.accounts import accounts as accounts
app.register_blueprint(accounts)
from app.irsystem import irsystem as irsystem
app.register_blueprint(irsystem)

# Initialize app w/SocketIO
socketio.init_app(app)

# HTTP error handling
@app.errorhandler(404)
def not_found(error):
  return render_template("404.html"), 404
