# PROCESSING
import re
from lists import stop_words, synonym_list, times, all_lists, fields_ori, names, bio_list, parties
from elasticsearch import Elasticsearch, helpers
import queries
from helper import calSimilarity_words

client = Elasticsearch(HOST="http://localhost", PORT=9200)
INDEX = 'index-ministers'


def stemmer(word):
    stem_dict = {"ගේ$": "", "^(සිටි||හිටි).$": "සිටි"}
    stemmed = word
    for k in stem_dict:
        stemmed = re.sub(k, stem_dict[k], stemmed)
    return stemmed


def preprocess(phrase):
    phrase_l = phrase.split()
    processed_phrase = []
    for word in phrase_l:
        stemmed_word = word
        if not word.isdigit():
            stemmed_word = stemmer(word)
        if stemmed_word not in stop_words:
            processed_phrase.append(stemmed_word)
    processed_s = " ".join(processed_phrase)
    return processed_s


def boost(boost_array):
    # views is not taken for search

    name = "name^{}".format(boost_array[1])
    position = "position^{}".format(boost_array[2])
    party = "party^{}".format(boost_array[3])
    district = "district^{}".format(boost_array[4])
    related_subjects = "related_subjects^{}".format(boost_array[5])
    biography = "biography^{}".format(boost_array[6])
    overall_rank = "overall_rank^{}".format(boost_array[7])
    party_rank = "party_rank^{}".format(boost_array[8])
    dob = "dob^{}".format(boost_array[9])

    return [name, position, party, district, related_subjects, biography, overall_rank, party_rank, dob]


def searchByName(tokens):
    c = 0
    for t in range(len(tokens)):
        token = tokens[t]
        for name in names:
            namel = name.split()
            for i in range(len(namel)):
                if calSimilarity_words(token, namel[i], 0.95) and abs(len(token)-len(namel[i])) <= 1:
                    tokens.append(namel[i])
                    c = 1
    if c:
        return True
    else:
        return False

def yearClassifier(tokens,flags,dob_flag,num):
    #containsDigit = bool(re.search(r'\d', processed_phrase))
    for each_token in tokens:
        if len(each_token) == 4 and each_token.isnumeric():
            containsDigit = False
            flags[9] = 5
            dob_flag = True
            break
        elif each_token.isnumeric():
            containsDigit = True
            num = each_token
            break
        else:
            containsDigit = False
    return containsDigit,flags,dob_flag,num

def boostFields(tokens,synonym_list,search_list):
    for word in tokens:
            for i in range(len(synonym_list)):
                if word in synonym_list[i]:
                    print('Boosting field', i, 'for', word,
                          'in synonym list - search by name')
                    search_list[i] = 1
                    break

    return search_list

def search_bio(phrase):
    # 0 - number
    # 1 - name
    # 2 - position
    # 3 - party
    # 4 - district
    # 5 - related_subjects
    # 6 - biography
    # 7 - overall_rank
    # 8 - party_rank
    # 9 - dob
    flags = [0, 1, 1, 1, 1, 1, 5, 1, 1, 1]
    fields = boost(flags)
    tokens = phrase.split()
    for t in range(len(tokens)):
        token = tokens[t]
        for p in bio_list:
            if calSimilarity_words(token, p, 0.8):
                tokens.append(p)
    phrase = " ".join(tokens)
    print(phrase)
    print(fields)
    query_body = queries.agg_multi_match_q(phrase, fields, operator='or')
    print('Making Faceted Query')
    res = client.search(index=INDEX, body=query_body)
    resl = res['hits']['hits']
    outputl = []
    for hit in resl:
        outputl.append([hit['_source']['name'], hit['_source']
                       ['biography'], hit['_score']])
    res = outputl
    return res


def search(phrase):
    # 0 - number
    # 1 - name
    # 2 - position
    # 3 - party
    # 4 - district
    # 5 - related_subjects
    # 6 - biography
    # 7 - overall_rank
    # 8 - party_rank
    # 9 - dob
    flags = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1]

    # search list
    # 0 - position
    # 1 - party
    # 2 - district
    # 3 - related_subjects
    # 4 - contact info
    # 5 - participation
    search_list = [0, 0, 0, 0, 0, 0]

    num = 0
    processed_phrase = preprocess(phrase)
    tokens = processed_phrase.split()
    search_by_name = searchByName(tokens)
    tokens = list(set(tokens))
    dob_flag = False

    containsDigit,flags,dob_flag,num = yearClassifier(tokens,flags,dob_flag,num)
    print(tokens)
    if search_by_name:
        print("Search By Name")
        flags[1] = 5
        search_list = boostFields(tokens,synonym_list,search_list)

    elif dob_flag:
        print("Saerch by Birth year")
        search_list = boostFields(tokens,synonym_list,search_list)

    elif containsDigit:
        print("Search by contains digit")
        flags[0] = 1
        #popularity = False
        participation = False
        print(tokens)
        similar_words = []
        for word in tokens:
            if word in times:
                op = "eql"
                participation = True
                break
            for term in parties:
                ts = term.split()
                for j in range(len(ts)):
                    if calSimilarity_words(word, ts[j]):
                        similar_words.append(ts[j])
                        flags[3] = 5
                        flags[8] = 5
        if flags[8] != 5 and flags[3] != 5:
          flags[7] = 5
    
    else:
        print("Search by others")
        # Identify numbers
        search_terms = []
        for w in range(len(tokens)):
            word = tokens[w]

            # Check whether a value from any list is present
            for i in range(len(all_lists)):
                l = all_lists[i]
                for term in l:
                    ts = term.split()
                    for j in range(len(ts)):
                        if calSimilarity_words(word, ts[j]):
                            # tokens[w] = ts[j]
                            search_terms.append(ts[j])
                            print('Boosting field', i+2, 'for',
                                  word, ts[j], 'in all list')
                            flags[i+2] = 5

            # Check whether token matches any synonyms
            for i in range(4):
                if word in synonym_list[i]:
                    print('Boosting field', i, 'for', word, 'in synonym list')
                    flags[i+2] = 5

            # Check whether full phrase is in any list - NEED THIS?
            # for i in range(2, 9):
            #     if phrase in all_lists[i]:
            #         print('Boosting field', i, 'for', phrase, 'in all list')
            #         flags[i] = 5
        tokens = search_terms

    fields = boost(flags)

    # If the query contain a number call sort query
    phrase = " ".join(tokens)
    print(phrase, fields, search_list)

    if flags[1] == 5:
        if search_list.count(1) > 0:
            required_field = fields_ori[search_list.index(1)]
            print("exact match with "+required_field)
            query_body = queries.exact_match(phrase, 'name', required_field)
            res = client.search(index=INDEX, body=query_body)
            resl = res['hits']['hits']
            outputl = []
            for hit in resl:
                ansl = hit["fields"][required_field]
                if (len(ansl) > 1):
                    out = " ; ".join(ansl)
                else:
                    out = ansl[0]
                outputl.append(
                    [hit['_source']['name']+" - " + str(out), hit['_score']])
            res = outputl
        else:
            query_body = queries.exact_match(phrase)
            res = client.search(index=INDEX, body=query_body)
            resl = res['hits']['hits']
            outputl = []
            for hit in resl:
                minister = hit['_source']
                name = minister["name"]
                position = minister["position"]
                party = minister["party"]
                district = minister["district"]
                contact = ";".join(minister["telephone"])
                related_subjects = ";".join(minister["related_subjects"])
                biography = minister["biography"]
                outputl.append([name, position, party, district,
                               contact, related_subjects, biography])
            res = outputl
    elif flags[0] == 1:
        if participation:
            print("participation exact match")
            required_field = "participated_in_parliament"
            query_body = queries.exact_match(
                phrase, required_field, search_val=int(num))
            res = client.search(index=INDEX, body=query_body)
            resl = res['hits']['hits']
            outputl = []
            for hit in resl:
                outputl.append(
                    hit['_source']['name']+" (" + str(hit['_source']['participated_in_parliament']) + " වතාවක්)")
            res = outputl
        else:
            if flags.count(5) == 2:
                # required_field = []
                # for each_flag in range(len(flags)):
                #     if flags[each_flag] == 5:
                #         required_field.append(fields_ori[each_flag-2])
                # print("cross")
                # print(required_field)
                phrase = similar_words[0] + " " + num
                print(phrase)
                query_body = queries.agg_multi_match_and_sort_q(phrase)
                res = client.search(index=INDEX, body=query_body)
                resl = res['hits']['hits']
                outputl = []
                for hit in resl:
                    outputl.append(hit['_source']['name'])
                res = outputl
            else:
                required_field = 'name'
                print("exact match with "+required_field)
                query_body = queries.exact_match(num, 'overall_rank', required_field)
                res = client.search(index=INDEX, body=query_body)
                resl = res['hits']['hits']
                outputl = []
                for hit in resl:
                    ansl = hit["fields"][required_field]
                    if (len(ansl) > 1):
                        out = " ; ".join(ansl)
                    else:
                        out = ansl[0]
                    outputl.append(
                        hit['_source']['name'])
                res = outputl

    else: 
        if dob_flag == True: # birth year related queries
            isAllZero = isListZero(search_list)
            print(isAllZero)
            if isAllZero == True:
                required_field = "name"
            else:
                required_field = fields_ori[search_list.index(1)]
            print("exact match with "+required_field)
            query_body = queries.exact_match(phrase, 'dob', required_field)
            res = client.search(index=INDEX, body=query_body)
            resl = res['hits']['hits']
            outputl = []
            for hit in resl:
                ansl = hit["fields"][required_field]
                if (len(ansl) > 1):
                    out = " ; ".join(ansl)
                else:
                    out = ansl[0]
                outputl.append(
                    [hit['_source']['name'], str(out)])
            res = outputl
        else:
            print('Making Faceted Query')
            query_body = queries.agg_multi_match_q(phrase, fields)
            required_field = fields_ori[flags.index(5)-2]
            res = client.search(index=INDEX, body=query_body)
            resl = res['hits']['hits']
            outputl = []
            for hit in resl:
                ansl = hit['_source'][required_field]
                if isinstance(ansl, list):
                    out = " ; ".join(ansl)
                else:
                    out = ansl
                outputl.append(
                    [hit['_source']['name'], str(out)])
            res = outputl
    return res

def isListZero(search_list):
    for value in search_list:
        if value == 1:
            return False
            break
    return True
        
