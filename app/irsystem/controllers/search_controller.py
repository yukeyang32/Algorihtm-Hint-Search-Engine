from . import *  
from app import leetcode_data, titleToTags, titleToURL, NON_HINT_TAGS
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from app.irsystem.models.search import *
from collections import defaultdict

project_name = "Leethelper"
net_id = "Wei Cheng - wc655 | Shuyi Gu - sg2474 | Tan Su - ts864 | Keyang Yu - ky442 | Jiejun Zhang - jz2252"

NUM_TOP_QUESTIONS = 5
NUM_TOP_HINTS = 5

def getSortedTopTags(topQuestions):
  MIN_Q_SCORE = 0.1
  totalRelevance = 0
  tagToScore = defaultdict(int)

  for title, _, score in topQuestions:
    if score >= MIN_Q_SCORE:
      totalRelevance += score

      for tag in titleToTags[title]:
        if tag not in NON_HINT_TAGS:
          tagToScore[tag] += score

  return sorted(((t, s / totalRelevance) for t, s in tagToScore.items()), key=lambda x: x[1], reverse=True)[:NUM_TOP_HINTS]

@irsystem.route('/', methods=['GET'])
def search():
  query = request.args.get('search')

  if not query:
    output_message = ''
    topQuestions = []
    topTags = []

  else:
    output_message = "Your search: " + query

    # Type: [(title, score)], not sorted by score.
    similarity_score_list = compute_cosine_similarity(query, leetcode_data)
    similarity_score_list.sort(key=lambda x: x[1], reverse=True)

    # Type: [(title, url, score)], sorted by score.
    topQuestions = [(t, titleToURL[t], s) for t, s in similarity_score_list[:NUM_TOP_QUESTIONS]]
    # Type: [(hint, score)], sorted by score.
    topHints = getSortedTopTags(topQuestions)

    print()
    print(topQuestions) 
    print(topHints)
    print()

  return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=topQuestions)
