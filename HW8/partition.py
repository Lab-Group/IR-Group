import os
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans


# =========================
# LOAD CRANFIELD DATASET
# =========================

DATASET_PATH = os.path.join(
    "..",
    "cranfield-trec-dataset-main",
    "cran.all.1400.xml"
)

print("Loading Cranfield dataset...")

with open(DATASET_PATH, "r", encoding="utf-8", errors="ignore") as f:
    data = f.read()


# =========================
# PARSE DOCUMENTS
# =========================

docs_raw = re.findall(r"<doc>(.*?)</doc>", data, re.DOTALL)

doc_ids = []
documents = []

for doc in docs_raw:

    docno = re.search(r"<docno>(.*?)</docno>", doc)

    if docno:
        doc_id = docno.group(1).strip()

        # remove tags and keep text
        text = re.sub(r"<.*?>", " ", doc)

        doc_ids.append(doc_id)
        documents.append(text)


print("Total documents loaded:", len(documents))


# =========================
# TF-IDF VECTORIZATION
# =========================

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=5000
)

X = vectorizer.fit_transform(documents)


# =========================
# PARTITION CLUSTERING
# =========================

K = 8

model = KMeans(
    n_clusters=K,
    random_state=42,
    n_init=10
)

labels = model.fit_predict(X)


# =========================
# STORE CLUSTERS
# =========================

clusters = {i: [] for i in range(K)}

for i, label in enumerate(labels):
    clusters[label].append(doc_ids[i])


# =========================
# SAVE RESULTS
# =========================

with open("partition_output.txt", "w", encoding="utf-8") as f:

    for c in clusters:
        f.write(f"\nCluster {c+1}:\n")
        f.write(" ".join(clusters[c]))
        f.write("\n")


print("Partition clustering completed successfully!")
print("Saved to partition_output.txt")