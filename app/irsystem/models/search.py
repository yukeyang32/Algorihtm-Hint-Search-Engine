import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('stopwords')
sw = stopwords.words('english') 

def compute_cosine_similarity(query,data):
    result = list()
    query_vec = word_tokenize(query)
    for index, dat in data.iterrows():
        dat_vec = word_tokenize(dat['description'])
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
        
