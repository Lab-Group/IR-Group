with open("cranqrel", "r") as fin, open("qrels.txt", "w") as fout:
    for line in fin:
        parts = line.split()
        if len(parts) >= 3:
            qid = parts[0]
            docid = parts[1]
            rel = parts[2]

            rel_binary = "1" if rel in ["1", "2", "3", "4"] else "0"

            fout.write(f"{qid} 0 {docid} {rel_binary}\n")

print("qrels.txt created successfully")