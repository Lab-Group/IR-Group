import re
import dill
from collections import defaultdict
from stemming.porter2 import stem

# =========================
# FILE PATHS
# =========================
DOC_FILE = r"cranfield-trec-dataset-main/cran.all.1400.xml"
INDEX_PATH = "inverted_index.p"
DOCMAP_PATH = "docMap.p"
DOC_LENGTHS_PATH = "doc_lengths.p"

# =========================
# STOPWORDS
# =========================
stopWords = {
    "a","an","the","is","are","was","were",
    "in","on","of","to","and","for","with"
}

# =========================
# TOKENIZER
# =========================
def tokenize(text):
    words = re.findall(r"[a-z]+", text.lower())
    return [stem(w) for w in words if w not in stopWords and len(w) > 2]

# =========================
# BUILD INDEX
# =========================
def build():
    print("READING DOCUMENTS...")

    index = defaultdict(lambda: defaultdict(lambda: {"tf": 0, "pos": []}))
    doc_map = {}
    doc_lengths = {}

    with open(DOC_FILE, "r", encoding="utf-8", errors="ignore") as f:
        data = f.read()

    docs = re.findall(r"<doc>(.*?)</doc>", data, re.DOTALL)

    for doc_id, doc in enumerate(docs, start=1):

        doc_map[doc_id] = f"doc_{doc_id}"

        text = re.sub(r"<.*?>", " ", doc)
        tokens = tokenize(text)

        doc_lengths[doc_id] = len(tokens)

        for pos, term in enumerate(tokens):
            entry = index[term][doc_id]
            entry["tf"] += 1
            entry["pos"].append(pos)

        if doc_id % 100 == 0:
            print(f"Indexed {doc_id} documents")

    print("DONE INDEXING")
    print("DOCS:", len(doc_map))
    print("TERMS:", len(index))

    print("SAVING FILES...")

    with open(INDEX_PATH, "wb") as f:
        dill.dump(dict(index), f)

    with open(DOCMAP_PATH, "wb") as f:
        dill.dump(doc_map, f)

    with open(DOC_LENGTHS_PATH, "wb") as f:
        dill.dump(doc_lengths, f)

    print("SAVE COMPLETE")

# =========================
if __name__ == "__main__":
    build()