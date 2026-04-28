import math

graphPages = {}
d = 0.85


class Page:
    def __init__(self, page):
        self.page = page
        self.rank = 0.0
        self.inLinkPages = []
        self.noOfOutLinks = 0


# =========================
# LOAD GRAPH
# =========================
def initializegraphPages(graphFile):
    with open(graphFile, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 0:
                continue

            parent = parts[0]
            children = parts[1:]

            if parent not in graphPages:
                graphPages[parent] = Page(parent)

            graphPages[parent].inLinkPages = children

            for c in children:
                if c not in graphPages:
                    graphPages[c] = Page(c)
                graphPages[c].noOfOutLinks += 1

    # initialize ranks
    N = len(graphPages)
    for p in graphPages:
        graphPages[p].rank = 1.0 / N


# =========================
# SINK NODES
# =========================
def getSinkNodes():
    return {p for p in graphPages if graphPages[p].noOfOutLinks == 0}


# =========================
# PAGE RANK CALC
# =========================
def calculatePageRank():
    sinkNodes = getSinkNodes()
    sinkPR = sum(graphPages[p].rank for p in sinkNodes)

    N = len(graphPages)
    newRanks = {}

    for p in graphPages:
        newRank = (1 - d) / N
        newRank += d * sinkPR / N

        for q in graphPages[p].inLinkPages:
            if q in graphPages and graphPages[q].noOfOutLinks > 0:
                newRank += d * graphPages[q].rank / graphPages[q].noOfOutLinks

        newRanks[p] = newRank

    for p in graphPages:
        graphPages[p].rank = newRanks[p]


# =========================
# MAIN
# =========================
initializegraphPages("linkgraph.txt")

N = len(graphPages)
print("Total nodes:", N)

prev = 0
convergence = 0
iteration = 0

while convergence < 4:
    calculatePageRank()

    entropy = 0
    for p in graphPages:
        r = graphPages[p].rank
        entropy += r * math.log(r + 1e-12, 2)

    perplexity = 2 ** (-entropy)

    if abs(perplexity - prev) < 1:
        convergence += 1
    else:
        convergence = 0

    prev = perplexity
    iteration += 1

print("Iterations:", iteration)

# =========================
# OUTPUT
# =========================
with open("pagerank_output.txt", "w", encoding="utf-8") as f:
    ranked = sorted(graphPages.items(), key=lambda x: x[1].rank, reverse=True)

    for i, (p, obj) in enumerate(ranked[:500]):
        f.write(f"{p} {obj.rank} {len(obj.inLinkPages)}\n")

print("PageRank completed!")