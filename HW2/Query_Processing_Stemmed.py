import re
import math
import dill
from collections import defaultdict
from stemming.porter2 import stem

# =========================
# SETTINGS
# =========================
INDEX_PATH = "inverted_index.p"
DOC_LENGTHS_PATH = "doc_lengths.p"
QUERY_FILE = r"C:\Users\fikir\Downloads\Telegram Desktop\cranfield-trec-dataset-main\cranfield-trec-dataset-main\cran.qry.xml"

N = 1400
k1 = 1.5
b = 0.75

stopWords = {
    "a","an","the","is","are","was","were",
    "in","on","of","to","and","for","with"
}

# =========================
# LOAD DATA
# =========================
def load_index():
    with open(INDEX_PATH, "rb") as f:
        return dill.load(f)

def load_doc_lengths():
    with open(DOC_LENGTHS_PATH, "rb") as f:
        return dill.load(f)

def load_queries():
    queries = {}
    with open(QUERY_FILE, "r", encoding="utf-8", errors="ignore") as f:
        data = f.read()

    blocks = re.findall(r"<top>(.*?)</top>", data, re.DOTALL)

    for block in blocks:
        num = re.search(r"<num>\s*(\d+)", block)
        title = re.search(r"<title>(.*?)</title>", block, re.DOTALL)

        if num and title:
            qid = int(num.group(1))
            queries[qid] = title.group(1).strip()

    return queries

# =========================
# TOKENIZER
# =========================
def tokenize(text):
    words = re.findall(r"[a-z]+", text.lower())
    return [stem(w) for w in words if w not in stopWords and len(w) > 2]

# =========================
# PROXIMITY
# =========================
def proximity_score(terms, index):
    scores = defaultdict(float)

    for i in range(len(terms)):
        for j in range(i + 1, len(terms)):
            t1, t2 = terms[i], terms[j]

            if t1 not in index or t2 not in index:
                continue

            docs1 = index[t1]
            docs2 = index[t2]

            common = set(docs1.keys()) & set(docs2.keys())

            for doc in common:
                pos1 = docs1[doc]["pos"]
                pos2 = docs2[doc]["pos"]

                if not pos1 or not pos2:
                    continue

                min_dist = min(abs(a - b) for a in pos1 for b in pos2)
                scores[doc] += 1 / (min_dist + 1)

    return scores

# =========================
# BM25
# =========================
def score(query, index, doc_lengths):
    terms = tokenize(query)
    scores = defaultdict(float)

    avgdl = sum(doc_lengths.values()) / len(doc_lengths)

    for term in terms:
        if term not in index:
            continue

        postings = index[term]
        df = len(postings)

        idf = math.log((N - df + 0.5) / (df + 0.5) + 1)

        for doc, data in postings.items():
            tf = data["tf"]
            dl = doc_lengths.get(doc, 1)

            bm25 = ((k1 + 1) * tf) / (
                k1 * ((1 - b) + b * (dl / avgdl)) + tf
            )

            scores[doc] += idf * bm25

    # proximity boost
    prox = proximity_score(terms, index)
    for doc, val in prox.items():
        scores[doc] += val

    return scores

# =========================
# RUN + WRITE FILE
# =========================
def run():
    print("LOADING INDEX...")
    index = load_index()
    print("INDEX TERMS:", len(index))

    print("LOADING DOC LENGTHS...")
    doc_lengths = load_doc_lengths()
    print("DOCS:", len(doc_lengths))

    queries = load_queries()
    print("QUERIES:", len(queries))

    results_file = open("results.txt", "w")

    for qid, qtext in queries.items():
        scores = score(qtext, index, doc_lengths)

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]

        print(f"\nQUERY {qid}")
        print(ranked)

        for rank, (doc, score_val) in enumerate(ranked, start=1):
            results_file.write(f"{qid} Q0 {doc} {rank} {score_val:.4f} run1\n")

    results_file.close()
    print("\nresults.txt saved successfully")

# =========================
if __name__ == "__main__":
    run()