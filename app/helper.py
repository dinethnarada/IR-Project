import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from lists import names

# search = "කුලසිංහම් දිලීපන් මහතාගේ තනතුර"
def calSimilarity(search):
    search_term_list = search.split()
    name_terms = []
    search_val = []
    for name in names:
        name_terms += [i for i in name.split() if len(i)>1 and '.' not in i]
    for j in search_term_list : 
        documents = [j]
        documents.extend(name_terms)
        tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
        tfidf_matrix = tfidf_vectorizer.fit_transform(documents)

        cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)
        similarity_list = cs[0][1:]
        # print(j, similarity_list)
        max_val = max(similarity_list)
        if max_val > 0.9 :
            loc = np.where(similarity_list==max_val)
            i = loc[0][0]
            search_val.append(name_terms[i])
    return search_val

def calSimilarity_words(w1,w2,thr=0.7):
    documents = [w1,w2]
    tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents)

    cs = cosine_similarity(tfidf_matrix[0],tfidf_matrix[1])
    if cs[0] > thr:
        return True
    else:
        return False
