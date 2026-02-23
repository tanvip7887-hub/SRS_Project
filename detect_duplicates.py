import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer


THRESHOLD = 0.85


# -----------------------------------------
# STEP 1 — Load Requirements
# -----------------------------------------

def load_requirements(path="requirements.json"):
    print("\n🟢 Loading requirements...")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Total requirements: {len(data)}")
    return data


# -----------------------------------------
# STEP 2 — Generate Embeddings
# -----------------------------------------

def generate_embeddings(requirements):
    print("\n🟡 Loading MiniLM model...")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    print("Generating embeddings...")
    texts = list(requirements.values())
    embeddings = model.encode(texts, convert_to_numpy=True)

    print("Embeddings shape:", embeddings.shape)
    return embeddings


# -----------------------------------------
# STEP 3 — Compute Cosine Similarity Matrix
# -----------------------------------------

def compute_similarity(embeddings):
    print("\n🟠 Computing cosine similarity matrix...")
    sim_matrix = cosine_similarity(embeddings)
    print("Similarity matrix shape:", sim_matrix.shape)
    return sim_matrix


# -----------------------------------------
# STEP 4 — Graph-Based Duplicate Detection
# -----------------------------------------

def find_duplicate_groups(req_ids, sim_matrix):
    print("\n🔵 Finding duplicate groups using graph clustering...")

    n = len(req_ids)
    visited = set()
    groups = []

    for i in range(n):
        if i in visited:
            continue

        stack = [i]
        component = []

        while stack:
            node = stack.pop()
            if node in visited:
                continue

            visited.add(node)
            component.append(node)

            for j in range(n):
                if j not in visited and sim_matrix[node][j] >= THRESHOLD:
                    stack.append(j)

        if len(component) > 1:
            groups.append(component)

    print(f"Duplicate groups found: {len(groups)}")
    return groups


# -----------------------------------------
# STEP 5 — Convert to Clean JSON Structure
# -----------------------------------------

def build_grouped_output(groups, req_ids, sim_matrix):
    duplicate_groups = {}

    for group in groups:
        base_id = req_ids[group[0]]
        duplicates = {}

        for idx in group[1:]:
            duplicates[req_ids[idx]] = round(
                float(sim_matrix[group[0]][idx]), 4
            )

        duplicate_groups[base_id] = duplicates

    return duplicate_groups


# -----------------------------------------
# STEP 6 — Save Results
# -----------------------------------------

def save_results(data):
    with open("duplicates_grouped.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    with open("duplicates_readable.txt", "w", encoding="utf-8") as f:
        for base, group in data.items():
            f.write(f"\n{base}:\n")
            for dup_id, score in group.items():
                f.write(f"   • {dup_id} ({score})\n")

    print("\n🟣 Saved:")
    print(" - duplicates_grouped.json")
    print(" - duplicates_readable.txt")


# -----------------------------------------
# MAIN PIPELINE
# -----------------------------------------

if __name__ == "__main__":
    requirements = load_requirements()
    req_ids = list(requirements.keys())

    embeddings = generate_embeddings(requirements)
    sim_matrix = compute_similarity(embeddings)

    groups = find_duplicate_groups(req_ids, sim_matrix)
    grouped_output = build_grouped_output(groups, req_ids, sim_matrix)

    save_results(grouped_output)

    print("\n🔴 SAMPLE OUTPUT:")
    for k, v in list(grouped_output.items())[:5]:
        print(f"\n{k}:")
        for dup, score in v.items():
            print(f"   → {dup} ({score})")