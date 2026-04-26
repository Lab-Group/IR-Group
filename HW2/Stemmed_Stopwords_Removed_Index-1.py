from stemming.porter2 import stem
import time
from bs4 import BeautifulSoup
import os
import re
from collections import defaultdict
import dill

# =========================
# DATA STRUCTURE
# =========================
class TermVector:
    def __init__(self, tf=0, pos=None):
        self.tf = tf
        self.pos = pos if pos else []

# =========================
# SETTINGS (CHANGE ONLY THIS)
# =========================
DATA_PATH = r"C:\Users\fikir\Downloads\Telegram Desktop\cranfield-trec-dataset-main\cranfield-trec-dataset-main\cran.all.1400.xml"

stopWords = {
    "a","an","the","is","are","was","were",
    "in","on","of","to","and","for","with"
}

# =========================
# GLOBAL INDEX
# =========================
inverted_index = defaultdict(lambda: defaultdict(lambda: TermVector(0, [])))

docMap = {}
docID_counter = 0

# =========================
# TOKENIZER
# =========================
def tokenize(text):
    words = re.findall(r'\w+', text.lower())
    words = [w for w in words if w not in stopWords]
    words = [stem(w) for w in words]
    return words

# =========================
# READ DOCS
# =========================
def load_docs():
    with open(DATA_PATH, encoding="utf-8", errors="ignore") as f:
        data = f.read()

    # wrap safely in root (IMPORTANT FIX)
    soup = BeautifulSoup("<root>" + data + "</root>", "xml")

    # try multiple tag styles
    docs = soup.find_all(["doc", "DOC"])

    return docs

# =========================
# BUILD INDEX
# =========================
def build_index():
    global docID_counter

    docs = load_docs()

    for doc in docs:
        docno = doc.find("docno")
        if not docno:
            continue

        doc_name = docno.text.strip()

        if doc_name not in docMap:
            docID_counter += 1
            docMap[doc_name] = docID_counter

        doc_id = docMap[doc_name]

        text = doc.get_text()
        tokens = tokenize(text)

        for pos, term in enumerate(tokens, start=1):
            tv = inverted_index[term][doc_id]
            tv.tf += 1
            tv.pos.append(pos)

    print("Indexing done.")
    print("Docs:", len(docMap))
    print("Terms:", len(inverted_index))

# =========================
# SAVE INDEX
# =========================
def save():
    with open("inverted_index.p", "wb") as f:
        dill.dump(dict(inverted_index), f)

    with open("docMap.p", "wb") as f:
        dill.dump(docMap, f)

# =========================
# RUN
# =========================
if __name__ == "__main__":
    start = time.time()
    build_index()
    save()
    print("TIME:", time.time() - start)