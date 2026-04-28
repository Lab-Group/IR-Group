import os
import re
import time
from bs4 import BeautifulSoup
from collections import defaultdict

DATA_PATH = r"C:\Users\fikir\Downloads\Telegram Desktop\cranfield-trec-dataset-main\cranfield-trec-dataset-main"
DOC_PATH = DATA_PATH + r"\cran.all.1400.xml"

class TermVector:
    def __init__(self):
        self.tf = 0
        self.pos = []

def tokenizer(text):
    return re.findall(r"[a-z0-9]+", text.lower())

def load_documents(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        data = f.read()

    print("FILE START PREVIEW:")
    print(data[:500])  # 👈 IMPORTANT CHECK

    soup = BeautifulSoup(data, "lxml")

    docs = soup.find_all(re.compile("doc", re.I))
    print("Found doc tags:", len(docs))

    corpus = []

    for doc in docs:
        docno = doc.find("docno")
        text = doc.get_text()

        if docno:
            corpus.append((docno.text.strip(), text))

    return corpus

def build_index(docs):
    index = defaultdict(lambda: defaultdict(TermVector))

    for doc_id, text in docs:
        tokens = tokenizer(text)

        for pos, term in enumerate(tokens):
            if doc_id not in index[term]:
                index[term][doc_id] = TermVector()

            index[term][doc_id].tf += 1
            index[term][doc_id].pos.append(pos)

    return index

def main():
    start = time.time()

    print("Loading documents...")
    docs = load_documents(DOC_PATH)
    print("Total docs:", len(docs))

    print("Building index...")
    index = build_index(docs)

    print("Index built with", len(index), "terms")

    end = time.time()
    print("Time:", end - start, "seconds")

    sample_term = list(index.keys())[0]
    print("\nSample term:", sample_term)
    print("Docs:", list(index[sample_term].keys())[:5])

if __name__ == "__main__":
    main()