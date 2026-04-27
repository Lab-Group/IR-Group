from bs4 import BeautifulSoup
import re
from collections import defaultdict

# =========================
# DATASET PATH
# =========================
DATASET_PATH = "../cranfield-trec-dataset-main/cran.all.1400.xml"

# =========================
# LOAD DATASET
# =========================
with open(DATASET_PATH, "r", encoding="utf-8", errors="ignore") as f:
    data = f.read()
docs = re.findall(r"<doc>(.*?)</doc>", data, re.DOTALL)

documents = {}

for doc in docs:

    docno_match = re.search(r"<docno>(.*?)</docno>", doc)

    if docno_match:
        doc_id = docno_match.group(1).strip()

        text = re.sub(r"<.*?>", " ", doc)

        documents[doc_id] = text
# =========================
# TOKENIZER
# =========================
def tokenize(text):
    return set(re.findall(r"[a-z]+", text.lower()))

# =========================
# BUILD GRAPH (SIMILARITY GRAPH)
# =========================
graph = defaultdict(set)

doc_ids = list(documents.keys())

# IMPORTANT: ensure all nodes exist
for doc_id in doc_ids:
    graph[doc_id] = set()

for i in range(len(doc_ids)):
    for j in range(i + 1, len(doc_ids)):

        d1 = doc_ids[i]
        d2 = doc_ids[j]

        words1 = tokenize(documents[d1])
        words2 = tokenize(documents[d2])

        # similarity condition (tunable)
        if len(words1.intersection(words2)) > 5:
            graph[d1].add(d2)
            graph[d2].add(d1)

# =========================
# SAVE LINK GRAPH
# =========================
with open("linkgraph.txt", "w", encoding="utf-8") as f:
    for node in graph:
        line = node

        if graph[node]:
            line += " " + " ".join(graph[node])

        f.write(line + "\n")

print("Graph built successfully!")
print("Nodes:", len(graph))