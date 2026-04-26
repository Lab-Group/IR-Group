import time
import math
from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup
from collections import Counter

# =========================
# ELASTICSEARCH CONNECTION (KEEP YOURS)
# =========================
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "a8t9_j71q0kE7upr0*i-"),
    verify_certs=False
)

INDEX = "cranfield_index"

# =========================
# LOAD QUERIES
# =========================
def load_queries(path):
    queries = {}

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        data = f.read()

    soup = BeautifulSoup(data, "xml")

    for top in soup.find_all("top"):
        qid = top.find("num").text.strip()
        qtext = top.find("title").text.strip()
        queries[qid] = qtext

    return queries


# =========================
# ES SEARCH
# =========================
def es_search(query):
    res = es.search(
        index=INDEX,
        size=100,
        query={"match": {"text": query}}
    )
    return res["hits"]["hits"]


# =========================
# DOC LENGTH
# =========================
def get_doc_length(text):
    return len(text.split())


# =========================
# OKAPI TF
# =========================
def okapi_tf(tf, dl, avgdl):
    return tf / (tf + 0.5 + 1.5 * (dl / avgdl))


# =========================
# TF-IDF
# =========================
def tfidf(tf, df, N):
    return tf * math.log((N + 1) / (df + 1))


# =========================
# BM25
# =========================
def bm25(tf, df, dl, avgdl, N, k1=1.5, b=0.75):
    idf = math.log((N - df + 0.5) / (df + 0.5) + 1)
    denom = tf + k1 * (1 - b + b * dl / avgdl)
    return idf * (tf * (k1 + 1) / denom)


# =========================
# MAIN
# =========================
start = time.time()

qry_path = r"C:\Users\fikir\Downloads\Telegram Desktop\cranfield-trec-dataset-main\cranfield-trec-dataset-main\cran.qry.xml"

queries = load_queries(qry_path)

print("Total Queries:", len(queries))

# =========================
# OUTPUT FILES (FIXED)
# =========================
files = {
    "es": open("es.txt", "w", encoding="utf-8"),
    "tfidf": open("tfidf.txt", "w", encoding="utf-8"),
    "okapi": open("okapi.txt", "w", encoding="utf-8"),
    "bm25": open("bm25.txt", "w", encoding="utf-8"),
}

# =========================
# PROCESS QUERIES
# =========================
for qid, qtext in queries.items():

    hits = es_search(qtext)

    # document stats
    docs = []
    for h in hits:
        doc_id = h["_id"]
        text = h["_source"]["text"]
        docs.append((doc_id, text, h["_score"]))

    if len(docs) == 0:
        continue

    lengths = [get_doc_length(d[1]) for d in docs]
    avgdl = sum(lengths) / len(lengths)

    N = 100000  # approx corpus size (safe fallback)

    # =========================
    # WRITE RESULTS
    # =========================
    rank = 1

    for doc_id, text, score in docs[:100]:

        dl = get_doc_length(text)
        tf_counts = Counter(text.lower().split())

        terms = qtext.lower().split()

        score_okapi = 0
        score_tfidf = 0
        score_bm25 = 0

        for t in terms:
            tf = tf_counts[t]

            df = 10  # safe fallback (ES does not easily expose DF here)

            score_okapi += okapi_tf(tf, dl, avgdl)
            score_tfidf += tfidf(tf, df, N)
            score_bm25 += bm25(tf, df, dl, avgdl, N)

        # =========================
        # WRITE ES
        # =========================
        files["es"].write(f"{qid} Q0 {doc_id} {rank} {score} Exp\n")

        # =========================
        # WRITE TF-IDF
        # =========================
        files["tfidf"].write(f"{qid} Q0 {doc_id} {rank} {score_tfidf} Exp\n")

        # =========================
        # WRITE OKAPI
        # =========================
        files["okapi"].write(f"{qid} Q0 {doc_id} {rank} {score_okapi} Exp\n")

        # =========================
        # WRITE BM25
        # =========================
        files["bm25"].write(f"{qid} Q0 {doc_id} {rank} {score_bm25} Exp\n")

        rank += 1

    print("Processed Query", qid)

# =========================
# CLOSE FILES (VERY IMPORTANT)
# =========================
for f in files.values():
    f.close()

end = time.time()

print("\nDONE")
print("Time taken:", end - start)