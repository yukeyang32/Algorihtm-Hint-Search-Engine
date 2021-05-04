from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from app import idf, inv_idx, question_norms, index_to_title, tokenize
from collections import Counter, defaultdict
from functools import lru_cache
import math
import wikipedia
from app.irsystem.models.helpers import wikipediaEdgeCase

sw = stopwords.words('english') 

"""
All similarity measures should have return type [(title, score)], not sorted by score.
"""

def compute_cosine_similarity(query,data):
    result = list()
    query_vec = tokenize(query.lower())
    for index, dat in data.iterrows():
        dat_vec = tokenize(dat['description'].lower())
        # remove stop words
        query_set = {word for word in query_vec if not word in sw} 
        dat_set = {word for word in dat_vec if not word in sw}
        rvector = query_set.union(dat_set) 
        l1 = list()
        l2 = list()
        for w in rvector:
            if w in query_set: 
                l1.append(1)
            else: 
                l1.append(0)
            if w in dat_set: 
                l2.append(1)
            else: 
                l2.append(0)
        
        cosine_similarity = 0
        for i in range(len(rvector)):
            cosine_similarity += l1[i]*l2[i]
        cosine_similarity = cosine_similarity / float((sum(l1)*sum(l2))**0.5)
        result.append((dat['title'],cosine_similarity))
    return result

def compute_cosine_similarity_tf_idf(query):    
    index = inv_idx
    res = []
    query_toks = tokenize(query.lower())
    count_q = dict(Counter(query_toks))
    temp_score = defaultdict(lambda:0) # key: doc_id, value: q*d
    for query_term in count_q:
        if query_term not in index:
            continue
        query_term_indexs = index[query_term]
        for term_idx in query_term_indexs:
            doc_id = term_idx[0]
            term_freq = term_idx[1]
            temp_score[doc_id] += count_q[query_term] * idf[query_term] * term_freq * idf[query_term]     
    
    query_norms = 0
    for term in count_q:
        if term not in idf: 
            continue
        query_norms += (count_q[term]*idf[term])**2
    query_norms = math.sqrt(query_norms)
    for doc_id in temp_score:
        temp_score[doc_id] /= question_norms[doc_id]*query_norms
    
    score = [(index_to_title[k], v) for k, v in temp_score.items()]
    return score #sorted(score, key=lambda x:-x[1] )


@lru_cache(None)
def wikipedia_safe_summary_crawler(hint):
    try:
        # Edge case
        hint = wikipediaEdgeCase(hint)
        return wikipedia.summary(hint, sentences=2, auto_suggest = False)
    except wikipedia.exceptions.PageError as e:
        try:
            return wikipedia.summary(hint, sentences=2) 
        except:
            pass
    except wikipedia.DisambiguationError as e:
        try:
            hint = hint + " abstract data type"
            return wikipedia.summary(hint, sentences=2)
        except:
            pass

@lru_cache(None)
def wikipedia_safe_url_crawler(hint):
    try:
      # Edge case
        hint = wikipediaEdgeCase(hint)
        return wikipedia.page(hint, auto_suggest = False).url
    except wikipedia.exceptions.PageError as e:
      try:
        return wikipedia.page(hint).url 
      except:
        pass
    except wikipedia.DisambiguationError as e:
      try:
        hint = hint + " abstract data type"
        return wikipedia.page(hint).url
      except:
          pass
     
