import math
from collections import defaultdict

# ----------------------------
# LOAD QREL FILE
# ----------------------------
def load_qrels(path):
    qrels = defaultdict(dict)

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.split()

            qid = parts[0]
            docid = parts[2]
            rel = int(parts[3])

            qrels[qid][docid] = rel

    return qrels


# ----------------------------
# LOAD RUN FILE (your outputs)
# ----------------------------
def load_run(path):
    runs = defaultdict(list)

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.split()

            qid = parts[0]
            docid = parts[2]
            score = float(parts[4])

            runs[qid].append((docid, score))

    # sort by score desc
    for qid in runs:
        runs[qid].sort(key=lambda x: x[1], reverse=True)

    return runs


# ----------------------------
# PRECISION@K
# ----------------------------
def precision_at_k(ranked_list, qrels, k=10):
    if len(ranked_list) == 0:
        return 0

    top_k = ranked_list[:k]

    rel_count = 0
    for docid, _ in top_k:
        if qrels.get(docid, 0) > 0:
            rel_count += 1

    return rel_count / k


# ----------------------------
# AVERAGE PRECISION
# ----------------------------
def average_precision(ranked_list, qrels):
    hits = 0
    score = 0.0

    for i, (docid, _) in enumerate(ranked_list):
        if qrels.get(docid, 0) > 0:
            hits += 1
            score += hits / (i + 1)

    if hits == 0:
        return 0

    return score / hits


# ----------------------------
# MAIN EVAL
# ----------------------------
def evaluate(run_file, qrel_file):

    qrels = load_qrels(qrel_file)
    runs = load_run(run_file)

    map_scores = []
    p10_scores = []

    for qid in runs:

        ranked_list = runs[qid]
        rels = qrels.get(qid, {})

        ap = average_precision(ranked_list, rels)
        p10 = precision_at_k(ranked_list, rels, 10)

        map_scores.append(ap)
        p10_scores.append(p10)

        print(f"Query {qid} -> AP: {ap:.4f} | P@10: {p10:.4f}")

    print("\n========================")
    print("FINAL RESULTS")
    print("========================")
    print("MAP:", sum(map_scores) / len(map_scores))
    print("P@10:", sum(p10_scores) / len(p10_scores))


# ----------------------------
# RUN HERE
# ----------------------------
if __name__ == "__main__":

    qrel_file = "qrels.adhoc.51-100.AP89.txt"

    print("\nBM25 Evaluation")
    evaluate("bm25.txt", qrel_file)

    print("\nTF-IDF Evaluation")
    evaluate("tfidf.txt", qrel_file)

    print("\nES Evaluation")
    evaluate("es.txt", qrel_file)

    print("\nOKAPI Evaluation")
    evaluate("okapi.txt", qrel_file)

    print("\nLAPLACE Evaluation")
    evaluate("laplace.txt", qrel_file)