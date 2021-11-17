from elasticsearch import Elasticsearch, helpers
import json

es = Elasticsearch([{'host': 'localhost', 'port':9200}])

def data_upload():
    with open('data/data.json', encoding="utf8") as f:
        data = json.loads(f.read())
    helpers.bulk(es, data, index='index-ministers')
    print(es.indices.get_mapping())
    #es.indices.delete(index='index-ministers', ignore=[400, 404])



if __name__ == "__main__":
    data_upload()