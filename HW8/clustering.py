import os
import re
import math
from collections import defaultdict

# =========================
# 1. LOAD DATASET
# =========================
DATASET_PATH = os.path.join(
    "..",
    "cranfield-trec-dataset-main",
    "cran.all.1400.xml"
)

print("Loading dataset from:")
print(os.path.abspath(DATASET_PATH))

with open(DATASET_PATH, "r", encoding="utf-8", errors="ignore") as f:
    data = f.read()

# =========================
# FIXED PARSING (WORKING)
# =========================
docs_raw = re.findall(r"<doc>(.*?)</doc>", data, re.DOTALL)

documents = {}

for doc in docs_raw:
    docno = re.search(r"<docno>(.*?)</docno>", doc)
    text = re.sub(r"<.*?>", " ", doc)

    if docno:
        doc_id = docno.group(1).strip()
        documents[doc_id] = text

print("Total documents loaded:", len(documents))


# =========================
# SAFETY CHECK
# =========================
if len(documents) == 0:
    print("ERROR: No documents loaded!")
    exit()


# =========================
# 2. TOKENIZATION
# =========================
def tokenize(text):
    return re.findall(r"[a-z]+", text.lower())


# =========================
# 3. TF & DF
# =========================
tf = {}
df = defaultdict(int)

for doc_id, text in documents.items():
    words = tokenize(text)
    tf[doc_id] = {}

    unique_words = set(words)

    for w in words:
        tf[doc_id][w] = tf[doc_id].get(w, 0) + 1

    for w in unique_words:
        df[w] += 1


# =========================
# 4. TF-IDF
# =========================
N = len(documents)
tfidf = {}

for doc_id in tf:
    tfidf[doc_id] = {}

    for term in tf[doc_id]:
        tf_val = tf[doc_id][term]
        idf = math.log(N / (1 + df[term]))
        tfidf[doc_id][term] = tf_val * idf


# =========================
# 5. COSINE SIMILARITY
# =========================
def cosine(d1, d2):
    v1 = tfidf[d1]
    v2 = tfidf[d2]

    common = set(v1.keys()) & set(v2.keys())

    dot = sum(v1[t] * v2[t] for t in common)

    mag1 = math.sqrt(sum(x * x for x in v1.values()))
    mag2 = math.sqrt(sum(x * x for x in v2.values()))

    if mag1 == 0 or mag2 == 0:
        return 0

    return dot / (mag1 * mag2)


# =========================
# 6. K-MEANS CLUSTERING
# =========================
K = 5

doc_ids = list(documents.keys())

centroids = doc_ids[:K]
clusters = {}

for iteration in range(5):

    clusters = {i: [] for i in range(K)}

    # assign step
    for doc in doc_ids:

        best_cluster = 0
        best_score = -1

        for i in range(K):
            score = cosine(doc, centroids[i])
            if score > best_score:
                best_score = score
                best_cluster = i

        clusters[best_cluster].append(doc)

    # update step
    new_centroids = []

    for i in range(K):

        if len(clusters[i]) == 0:
            new_centroids.append(centroids[i])
            continue

        best_doc = clusters[i][0]
        best_score = -1

        for doc in clusters[i]:
            sim = sum(cosine(doc, other) for other in clusters[i])

            if sim > best_score:
                best_score = sim
                best_doc = doc

        new_centroids.append(best_doc)

    centroids = new_centroids


# =========================
# 7. OUTPUT
# =========================
with open("clusters_output.txt", "w", encoding="utf-8") as f:
    for i in clusters:
        f.write(f"\nCluster {i+1}:\n")
        f.write(" ".join(clusters[i]) + "\n")

print("Clustering completed successfully!")
print("Saved to clusters_output.txt")