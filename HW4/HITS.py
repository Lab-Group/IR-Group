import math

# =========================
# LOAD GRAPH
# =========================
graph = {}

with open("linkgraph.txt", "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 0:
            continue
        node = parts[0]
        links = parts[1:]
        graph[node] = set(links)

# ensure all nodes exist in graph (important!)
for node in list(graph.keys()):
    for out in graph[node]:
        if out not in graph:
            graph[out] = set()

# =========================
# INITIALIZE SCORES
# =========================
hubs = {node: 1.0 for node in graph}
auth = {node: 1.0 for node in graph}

# =========================
# HITS ITERATIONS
# =========================
for _ in range(10):

    # AUTHORITY UPDATE
    new_auth = {}
    for node in graph:
        new_auth[node] = 0.0
        for other in graph:
            if node in graph[other]:
                new_auth[node] += hubs[other]

    # HUB UPDATE
    new_hubs = {}
    for node in graph:
        new_hubs[node] = 0.0
        for out in graph[node]:
            new_hubs[node] += new_auth[out]

    # NORMALIZATION
    norm_auth = math.sqrt(sum(x * x for x in new_auth.values()))
    norm_hubs = math.sqrt(sum(x * x for x in new_hubs.values()))

    if norm_auth == 0: norm_auth = 1
    if norm_hubs == 0: norm_hubs = 1

    for node in graph:
        auth[node] = new_auth[node] / norm_auth
        hubs[node] = new_hubs[node] / norm_hubs

# =========================
# OUTPUT RESULTS
# =========================
with open("hits_output.txt", "w", encoding="utf-8") as f:
    sorted_nodes = sorted(auth.items(), key=lambda x: x[1], reverse=True)

    for node, score in sorted_nodes[:500]:
        f.write(f"{node} {score} {hubs[node]}\n")

print("HITS completed successfully!")