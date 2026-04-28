import time
import os
import re
from elasticsearch import Elasticsearch

# -----------------------------
# Elasticsearch connection
# -----------------------------
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "a8t9_j71q0kE7upr0*i-"),
    verify_certs=False
)

# -----------------------------
# Dataset path (safe & correct)
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(
    BASE_DIR,
    "..",
    "cranfield-trec-dataset-main",
    "cran.all.1400.xml"
)

# -----------------------------
# Start indexing
# -----------------------------
start_time = time.time()

# Read file as raw text (important for Cranfield dataset)
with open(DATASET_PATH, "r", encoding="utf-8", errors="ignore") as f:
    data = f.read()

# Extract all <doc> blocks using regex
docs = re.findall(r"<doc>(.*?)</doc>", data, re.DOTALL)

print("Total docs found:", len(docs))

i = 0

# -----------------------------
# Indexing loop
# -----------------------------
for d in docs:
    # extract doc id
    docno_match = re.search(r"<docno>(.*?)</docno>", d, re.DOTALL)

    # clean text (remove tags)
    text = re.sub(r"<.*?>", " ", d)

    if docno_match:
        doc_id = docno_match.group(1).strip()

        es.index(
            index="cranfield_index",
            id=doc_id,
            document={"text": text}
        )

        i += 1

        if i % 100 == 0:
            print("Indexed:", i)

# -----------------------------
# Done
# -----------------------------
print("Done indexing")
print("Total indexed:", i)

end_time = time.time()
print("Time:", end_time - start_time)