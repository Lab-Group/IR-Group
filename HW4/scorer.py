def score_evaluator(file_path, column_index):

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        score_holder = 0.0

        for line in f:
            parts = line.strip().split()

            if len(parts) <= column_index:
                continue

            try:
                score_holder += float(parts[column_index])
            except:
                continue

        return score_holder


# =========================
# MAIN
# =========================

file_path = "hits_output.txt"

hub_score = score_evaluator(file_path, 2)   # hub column
auth_score = score_evaluator(file_path, 1)  # authority column

print("Total hub score:", hub_score)
print("Total authority score:", auth_score)