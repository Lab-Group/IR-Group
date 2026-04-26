import os
import re
import math
import time
from bs4 import BeautifulSoup
from collections import defaultdict

# =========================
# PATHS (CHANGE IF NEEDED)
# =========================
DATA_PATH = r"C:\Users\fikir\Downloads\Telegram Desktop\cranfield-trec-dataset-main\cranfield-trec-dataset-main"

DOC_PATH = DATA_PATH + r"\cran.all.1400.xml"
QUERY_PATH = DATA_PATH + r"\cran.qry.xml"
QREL_PATH = DATA_PATH + r"\cranqrel.trec"

# =========================
# TOKENIZER
# =========================
def tokenize(text):
    return re.findall(r'\w+', text.lower())

# =========================
# LOAD DOCUMENTS
# =========================
def load_documents(path):
    print("Loading documents...")

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        data = f.read()

    # IMPORTANT FIX: use html parser (NOT xml)
    soup = BeautifulSoup(data, "html.parser")

    docs = soup.find_all("doc")

    corpus = {}
    doc_len = {}

    for doc in docs:
        docno = doc.find("docno")

        if docno:
            doc_id = docno.text.strip()

            # extract ONLY text field properly
            text_tag = doc.find("text")
            if text_tag:
                text = text_tag.get_text()
            else:
                text = doc.get_text()

            tokens = tokenize(text)

            corpus[doc_id] = tokens
            doc_len[doc_id] = len(tokens)

    print("Found docs:", len(corpus))
    return corpus, doc_len

# =========================
# INDEX STRUCTURE
# =========================
class TermVector:
    def __init__(self):
        self.tf = 0
        self.pos = []

# =========================
# BUILD INVERTED INDEX
# =========================
def build_index(corpus):
    index = defaultdict(lambda: defaultdict(TermVector))

    for doc_id, tokens in corpus.items():
        for pos, term in enumerate(tokens):
            index[term][doc_id].tf += 1
            index[term][doc_id].pos.append(pos)

    return index

# =========================
# LOAD QUERIES
# =========================
def load_queries(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        data = f.read()

    soup = BeautifulSoup(data, "xml")
    queries = {}

    for q in soup.find_all("top"):
        num = q.find("num")
        title = q.find("title")

        if num and title:
            qid = num.text.strip()
            qtext = title.text.strip()
            queries[qid] = qtext

    return queries

# =========================
# SCORING FUNCTIONS
# =========================
def okapi_tf(tf, dl, avg_dl):
    return tf / (tf + 0.5 + 1.5 * (dl / avg_dl))

def tfidf(tf, df, N, dl, avg_dl):
    return okapi_tf(tf, dl, avg_dl) * math.log((N + 1) / (df + 1))

def bm25(tf, df, N, dl, avg_dl, k1=1.5, b=0.75):
    idf = math.log((N + 0.5) / (df + 0.5))
    denom = tf + k1 * (1 - b + b * (dl / avg_dl))
    return idf * (tf * (k1 + 1)) / denom

# =========================
# PROXIMITY MODEL
# =========================
def proximity(query_terms, index):
    scores = defaultdict(float)

    valid = [t for t in query_terms if t in index]
    if len(valid) < 2:
        return scores

    docs = set(index[valid[0]].keys())
    for t in valid[1:]:
        docs &= set(index[t].keys())

    for d in docs:
        pos_lists = [index[t][d].pos for t in valid]

        min_span = float("inf")

        for p1 in pos_lists[0]:
            for p2 in pos_lists[1]:
                min_span = min(min_span, abs(p1 - p2))

        scores[d] = 1 / (min_span + 1)

    return scores

# =========================
# RUN QUERY
# =========================
def run_query(query, index, corpus, doc_len, model):
    scores = defaultdict(float)

    N = len(corpus)
    avg_dl = sum(doc_len.values()) / N

    terms = tokenize(query)

    for term in terms:
        if term not in index:
            continue

        df = len(index[term])

        for doc_id, vec in index[term].items():
            tf = vec.tf
            dl = doc_len[doc_id]

            if model == "okapi":
                scores[doc_id] += okapi_tf(tf, dl, avg_dl)

            elif model == "tfidf":
                scores[doc_id] += tfidf(tf, df, N, dl, avg_dl)

            elif model == "bm25":
                scores[doc_id] += bm25(tf, df, N, dl, avg_dl)

    if model == "proximity":
        scores = proximity(terms, index)

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

# =========================
# MAIN
# =========================
def main():
    start = time.time()

    corpus, doc_len = load_documents(DOC_PATH)
    print("Docs:", len(corpus))

    index = build_index(corpus)
    print("Terms:", len(index))

    queries = load_queries(QUERY_PATH)
    print("Queries:", len(queries))

    models = ["okapi", "tfidf", "bm25", "proximity"]

    for model in models:
        out = open(model + ".txt", "w")

        for qid, qtext in queries.items():
            results = run_query(qtext, index, corpus, doc_len, model)

            for rank, (doc_id, score) in enumerate(results[:100], 1):
                out.write(f"{qid} Q0 {doc_id} {rank} {score} Exp\n")

        out.close()
        print(model, "done")

    print("DONE in", time.time() - start)

if __name__ == "__main__":
    main()