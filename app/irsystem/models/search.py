from nltk.tokenize import word_tokenize


def compute_cosine_similarity(query,data):
    result = list()
    query_vec = word_tokenize(query)
    for index, dat in data.iterrows():
        dat_vec = word_tokenize(dat['description'])
        rvector = query_vec + dat_vec
        l1 = list()
        l2 = list()
        for w in rvector:
            if w in query_vec: 
                l1.append(1)
            else: 
                l1.append(0)
            if w in dat_vec: 
                l2.append(1)
            else: 
                l2.append(0)
        
        cosine_similarity = 0
        for i in range(len(rvector)):
            cosine_similarity += l1[i]*l2[i]
        cosine_similarity = cosine_similarity / float((sum(l1)*sum(l2))**0.5)
        result.append((dat['title'],cosine_similarity))
    return result
        
