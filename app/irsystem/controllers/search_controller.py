from wikipedia.wikipedia import suggest
from . import *  
from app import leetcode_data, titleToTags, titleToURL, NON_HINT_TAGS, titleToDifficulty, titleToDescription, titleToLike, titleToDislike, classify, wiki_data
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from app.irsystem.models.search import *
from collections import defaultdict
import numpy as np


project_name = "Leethelper"
net_id = "Wei Cheng - wc655 | Shuyi Gu - sg2474 | Tan Su - ts864 | Keyang Yu - ky442 | Jiejun Zhang - jz2252"

NUM_TOP_QUESTIONS = 6
NUM_TOP_HINTS = 6

def getScoreMultiplier(likes, dislikes):
  return (likes + 1) / (likes + dislikes + 1) * np.tanh(likes + dislikes + 1)

def getSortedTopTagsML(query):
  tags = classify(query)
  return [(t, s, wiki_data[t][1], wiki_data[t][0]) for t, s in tags[:NUM_TOP_HINTS]]

def getSortedTopTags(topQuestions):
  totalRelevance = 0
  tagToScore = defaultdict(int)

  for title, _, score, _, _, likes, dislikes in topQuestions:
    score *= getScoreMultiplier(likes, dislikes)
    totalRelevance += score

    for tag in titleToTags[title]:
      if tag not in NON_HINT_TAGS:
        tagToScore[tag] += score

  result =  sorted(((t, s / totalRelevance) for t, s in tagToScore.items()), key=lambda x: x[1], reverse=True)[:NUM_TOP_HINTS]
  result = [(t, s, wiki_data[t][1], wiki_data[t][0]) for t, s in result]
  return result

@irsystem.route('/', methods=['GET'])
def search():
  query = request.args.get('search')

  if not query:
    query = ''
    topQuestions = []
    topHints = []

  else:
    # Type: [(title, score)], not sorted by score.
    #similarity_score_list = compute_cosine_similarity(query, leetcode_data)
    similarity_score_list = compute_cosine_similarity_tf_idf(query)
    similarity_score_list.sort(key=lambda x: x[1], reverse=True)
    #print(similarity_score_list[:5])
    # Type: [(title, url, score, difficulty, description, likes, dislikes)], sorted by score.
    topQuestionsNoVote = [(t, titleToURL[t], s, titleToDifficulty[t], titleToDescription[t], titleToLike[t], titleToDislike[t]) for t, s in similarity_score_list[:NUM_TOP_QUESTIONS]]

    sim_score_list_with_vote = sorted([(t, s * getScoreMultiplier(titleToLike[t], titleToDislike[t])) for t, s in similarity_score_list[:NUM_TOP_QUESTIONS], key=lambda x: x[1], reverse=True)
    # Type: [(title, url, score, difficulty, description, likes, dislikes)], sorted by score.
    topQuestionsVote = [(t, titleToURL[t], s, titleToDifficulty[t], titleToDescription[t], titleToLike[t], titleToDislike[t]) for t, s in sim_score_list_with_vote]

    # Type: [(hint, score, summary, url)], sorted by score.
    # topHints = getSortedTopTags(topQuestions)
    topHints = getSortedTopTagsML(query)

    """
    print()
    print([(q, s) for q, _, s, _, _, _, _ in topQuestions]) 
    print()
    print([(t, s) for t, s, _, _ in topHints])
    print()
    """

  return render_template('search.html', name=project_name, netid=net_id, query=query, topQuestions=topQuestions, topHints=topHints)
