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
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize,RegexpTokenizer
from collections import defaultdict, Counter
import numpy as np
import math
import re


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
reg_tokenizer = RegexpTokenizer("[a-zA-Z][a-zA-Z]+")
def build_inverted_index(data):

  inverted_index = defaultdict(list)
  for index, dat in data.iterrows():
    dat_vec = reg_tokenizer.tokenize(dat['description'].lower())
    term_freq_in_dat = Counter(dat_vec)
    for term in term_freq_in_dat:
      inverted_index[term].append((index, term_freq_in_dat[term]))            
  return inverted_index
inv_idx = build_inverted_index(leetcode_data)
index_to_title = {idx:dat['title'] for idx,dat in leetcode_data.iterrows()}

def compute_idf(inv_idx, n_questions, min_df=15, max_df_ratio=0.90):
    
  idf = {}
  threshold = n_questions*max_df_ratio
  for term in inv_idx:
    if len(inv_idx[term]) > threshold or len(inv_idx[term]) < min_df:
      continue
    idf[term] = math.log2(n_questions / (1 + len(inv_idx[term])))
  return idf
idf = compute_idf(inv_idx, len(leetcode_data), min_df=1, max_df_ratio=0.1)

def compute_question_norms(index, idf, n_questions):
  norms = np.zeros(n_questions)
  for term in index:
    if term not in idf: 
      continue
    for term_inv_idx in index[term]:
      doc_id = term_inv_idx[0]
      term_freq_doc = term_inv_idx[1]
      norms[doc_id] += (term_freq_doc*idf[term])**2
  return np.sqrt(norms)

inv_idx = {key: val for key, val in inv_idx.items()
           if key in idf} 
question_norms = compute_question_norms(inv_idx, idf, len(leetcode_data))

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
