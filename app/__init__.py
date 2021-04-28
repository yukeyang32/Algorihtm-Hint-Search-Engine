# Gevent needed for sockets
from gevent import monkey
monkey.patch_all()

# Imports
import os
import ast
import math
import pickle
import re
import numpy as np
import pandas as pd

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize,RegexpTokenizer
from nltk.stem import WordNetLemmatizer, PorterStemmer

from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.neural_network import MLPRegressor
from sklearn.naive_bayes import MultinomialNB
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import train_test_split

from collections import defaultdict, Counter

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
titleToDifficulty = {}
titleToDescription = {}
titleToLike = {}
titleToDislike = {}

with open('./dataGeneration/wiki_data.pickle', 'rb') as f:
    wiki_data = pickle.load(f)
sw = set(stopwords.words('english'))

reg_tokenizer = RegexpTokenizer("[a-zA-Z]{2,}")
wnl = WordNetLemmatizer() #wnl.lemmatize(t)
ps = PorterStemmer() #ps.stem(t)

def tokenize(doc):
  return [ps.stem(t) for t in reg_tokenizer.tokenize(doc) if not t in sw]

def build_inverted_index(data):

  inverted_index = defaultdict(list)
  for index, dat in data.iterrows():
    dat_vec = tokenize(dat['description'].lower())
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
idf = compute_idf(inv_idx, len(leetcode_data), min_df=5, max_df_ratio=0.7)

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
  titleToDifficulty[d['title']] = d['difficulty']
  titleToDescription[d['title']] = d['description']
  titleToLike[d['title']] = d['likes']
  titleToDislike[d['title']] = d['dislikes']

# Train machine learning model
def trainClassifier():
  X = []
  Y = []

  for title, description in titleToDescription.items():
    tags = [t for t in titleToTags[title] if t not in NON_HINT_TAGS]

    if tags:
      X.append(description)
      Y.append(tags)

  mlVectorizer = TfidfVectorizer(tokenizer=tokenize, stop_words='english', max_df=0.7, min_df=5)
  X = mlVectorizer.fit_transform(X)

  classes = set()

  for tags in Y:
      for t in tags:
          classes.add(t)
          
  classes = list(classes)
  tagToClassIndex = {tag: i for i, tag in enumerate(classes)}

  for i in range(len(Y)):
      vectorY = [0] * len(classes)

      for tag in Y[i]:
          vectorY[tagToClassIndex[tag]] = 1

      Y[i] = vectorY

  Y = np.array(Y)
  clf = MultiOutputClassifier(MultinomialNB(fit_prior=False)).fit(X, Y)

  def classify(text):
    x = mlVectorizer.transform([text])
    class_probs = np.array([p[0][1] for p in clf.predict_proba(x)])
    return [(classes[i], class_probs[i]) for i in (-class_probs).argsort()]

  return classify

classify = trainClassifier()

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
