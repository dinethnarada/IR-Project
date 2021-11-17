# QUERIES
import json
from helper import calSimilarity


def agg_multi_match_q(query, fields=['title', 'song_lyrics'], operator='and'):
    q = {
        "size": 500,
        "explain": True,
        "query": {
            "multi_match": {
                "query": query,
                "fields": fields,
                "operator": operator,
                "type": "best_fields"
            }
        },
        "aggs": {
            "Position Filter": {
                "terms": {
                    "field": "position.keyword",
                    "size": 10
                }
            },
            "Party Filter": {
                "terms": {
                    "field": "party.keyword",
                    "size": 10
                }
            },
            "District Filter": {
                "terms": {
                    "field": "district.keyword",
                    "size": 10
                }
            },
            "Related Subjects Filter": {
                "terms": {
                    "field": "related_subjects.keyword",
                    "size": 10
                }
            },
            "Biography Filter": {
                "terms": {
                    "field": "biography.keyword",
                    "size": 10
                }
            }
        }
    }

    q = json.dumps(q)
    return q

def agg_multi_match_and_sort_q(query, fields=['party', 'party_rank'], comp_op=None):
    if comp_op == None:
        q = {
            "size": 500,
            "explain": True,
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ['party', 'party_rank'],
                    "type": "cross_fields",
                    "operator": "and"
                }
            },
        }
    else:
        q = {
            "size": 500,
            "query": {
                "range": {
                    "participated_in_parliament": {
                        comp_op: sort_num
                    }
                }
            },
            # "aggs":aggs
        }
    q = json.dumps(q)
    return q

def exact_match(query, field_name=None, required_field=None, search_val=None):
    if search_val:
        q = {
            "size": 500,
            "explain": True,
            "query": {
                "match": {
                    "participated_in_parliament": search_val
                }
            },
        }
    else:
        # search_val = " ".join(calSimilarity(query))
        if required_field:
            print("AAAA")
            q = {
                "size": 500,
                "explain": True,
                "query": {
                    "match": {
                        field_name: query
                    }
                },
                "fields": [required_field]
            }
        else:
            q = {
                "size": 500,
                "explain": True,
                "query": {
                    "match": {
                        "name": query
                    }
                },
            }
    q = json.dumps(q)

    return q
