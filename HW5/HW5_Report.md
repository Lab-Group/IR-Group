Here’s a **clean, shorter version** — balanced (not too long, not too basic):

---

# HW5 Report: TREC Evaluation

## Objective

The purpose of this assignment is to evaluate the performance of Information Retrieval (IR) models using standard TREC evaluation metrics. The goal is to measure how well each model retrieves and ranks relevant documents.

---

## Dataset

We used the **Cranfield dataset**, which includes:

* `cran.all.1400` (documents)
* `cran.qry` (queries)
* `cranqrel` (relevance judgments)

The relevance file was converted into TREC format (`qrels.txt`) for evaluation.

---

## Methodology

The evaluation was performed using two inputs:

* `qrels.txt` (ground truth relevance)
* `rankList.txt` (retrieval results)

Model outputs from previous assignments were used:

* **BM25**
* **TF-IDF**

Each model file was renamed to `rankList.txt` and evaluated using:

```bash
python Trec_Eval.py
```

Command used:

```
trec_eval qrels.txt rankList.txt
```

---

## Results

### BM25

* MAP: 0.0079
* R-Precision: 0.0116
* nDCG: 0.0719

### TF-IDF

* MAP: 0.0081
* R-Precision: 0.0116
* nDCG: 0.0691

---

## Comparison

| Metric      | BM25       | TF-IDF     | 
| ----------- | ---------- | ---------- |
| MAP         | 0.0079     | **0.0081** |
| R-Precision | 0.0116     | 0.0116     |
| nDCG        | **0.0719** | 0.0691     |

---

## Discussion

Both models show low performance overall. TF-IDF slightly outperforms BM25 in terms of Average Precision, meaning it retrieves relevant documents slightly better at the top ranks. However, BM25 has a higher nDCG, indicating slightly better ranking quality overall.

The results suggest that while both models can retrieve relevant documents, they are not very effective at ranking them properly.

---

## Conclusion

This assignment evaluated BM25 and TF-IDF using TREC metrics. Both models performed similarly, with only minor differences. Overall performance was low, indicating the need for better ranking techniques or model improvements.

 

 