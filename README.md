#  Search Engine for Sri Lankan Parliament Ministers

- Technology Stack
```
Flask Framework – For UI design
Scrapy Library – For data scrapping from website
Elasticsearch – For indexing document items
```

-  Steps to reproduce 

1. Install Docker from their [website](https://www.docker.com/products/docker-desktop)
2. Start an ElasticSearch Instance on the port 9200
3. Clone this repo and create a virtual environment
4. Install elastic-search
```
pip install elasticsearch
```
5. Install sklearn
```
pip install sklearn
```
6. Install flask
```
pip install flask
```
7. Run command ```python data_upload.py```
8. Run command ```flask run```
