from wikipedia.wikipedia import suggest
from . import *  
from app import leetcode_data, titleToTags, titleToURL, NON_HINT_TAGS, titleToDifficulty, titleToDescription, titleToLike, titleToDislike
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from app.irsystem.models.search import *
from collections import defaultdict



project_name = "Leethelper"
net_id = "Wei Cheng - wc655 | Shuyi Gu - sg2474 | Tan Su - ts864 | Keyang Yu - ky442 | Jiejun Zhang - jz2252"

NUM_TOP_QUESTIONS = 6
NUM_TOP_HINTS = 6



def getSortedTopTags(topQuestions):
  totalRelevance = 0
  tagToScore = defaultdict(int)

  for title, _, score, _, _, _, _ in topQuestions:
    totalRelevance += score

    for tag in titleToTags[title]:
      if tag not in NON_HINT_TAGS:
        tagToScore[tag] += score

  result =  sorted(((t, s / totalRelevance) for t, s in tagToScore.items()), key=lambda x: x[1], reverse=True)[:NUM_TOP_HINTS]
  result = [(t, s, wikipedia_safe_summary_crawler(t),  wikipedia_safe_url_crawler(t)  ) for t, s in result]
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

    # Type: [(title, url, score)], sorted by score.
    topQuestions = [(t, titleToURL[t], s, titleToDifficulty[t],titleToDescription[t], titleToLike[t], titleToDislike[t]) for t, s in similarity_score_list[:NUM_TOP_QUESTIONS]]
    # Type: [(hint, score)], sorted by score.
    topHints = getSortedTopTags(topQuestions)

    # print()
    # print(topQuestions) 
    # print(topHints)
    # print()

  return render_template('search.html', name=project_name, netid=net_id, query=query, topQuestions=topQuestions, topHints=topHints)
