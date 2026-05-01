import time
from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup
import os

es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "1R4Nfr=txQa1SdVxU3gh"),
    verify_certs=False
)
path = "Files/"
start_time = time.time()
i = 0

for filename in os.listdir(path):
    filepath = os.path.join(path, filename)
    if not os.path.isfile(filepath):
        continue
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            page = file.read()
        validPage = "<root>" + page + "</root>"
        soup = BeautifulSoup(validPage, 'html.parser')
        text = soup.find('text').get_text().strip()
        label = soup.find('label').get_text().strip()
        emailid = soup.find('emailid').get_text().strip()
        jsonDoc = {'text': text, 'label': label}
        es.index(index="hw7_index", id=emailid, body=jsonDoc)
        i += 1
        print("Indexed %d: %s" % (i, filename))
    except Exception as e:
        print("Skipped %s: %s" % (filename, e))

temp = time.time() - start_time
print("Done! Total indexed: %d" % i)
print("Time: %d:%d:%d" % (temp // 3600, (temp % 3600) // 60, temp % 60))
