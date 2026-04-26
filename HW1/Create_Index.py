from bs4 import BeautifulSoup
import time
from elasticsearch import Elasticsearch

es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "a8t9_j71q0kE7upr0*i-"),
    verify_certs=False
)

path = r"C:\Users\fikir\Downloads\Telegram Desktop\cranfield-trec-dataset-main\cranfield-trec-dataset-main\cran.all.1400.xml"

start_time = time.time()

with open(path, "r", encoding="utf-8", errors="ignore") as file:
    data = file.read()

# wrap in root because XML is not always single-rooted
soup = BeautifulSoup(data, "xml")

docs = soup.find_all("doc")

i = 0

for doc in docs:
    doc_id = doc.find("docno")
    text = doc.get_text(separator=" ")

    if doc_id:
        jsonDoc = {
            "text": text
        }

        es.index(
            index="cranfield_index",
            id=doc_id.text.strip(),
            document=jsonDoc
        )

        i += 1
        print("Indexed:", i)

print("Done indexing")

end_time = time.time()
print("Time:", end_time - start_time)