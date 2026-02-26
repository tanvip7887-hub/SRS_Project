import json
from sentence_transformers import util
from embedding_model import get_embeddings

# ==============================
# SETTINGS
# ==============================
SIMILARITY_THRESHOLD = 0.85  # Tune 0.83–0.88

print("📂 Loading requirements.json...")

# ==============================
# LOAD REQUIREMENTS (DICT FORMAT)
# ==============================
with open("requirements.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Your format: {"FR-01": "text", ...}
if not isinstance(data, dict):
    raise ValueError("requirements.json must be a dictionary of ID: text")

# Convert dictionary to list of dicts
requirements = []
for req_id, text in data.items():
    requirements.append({
        "id": req_id,
        "text": text.strip()
    })

print(f"🔢 Total requirements: {len(requirements)}")

texts = [req["text"] for req in requirements]

# ==============================
# GENERATE EMBEDDINGS
# ==============================
print("🧠 Generating embeddings...")
embeddings = get_embeddings(texts)

# ==============================
# CALCULATE SIMILARITY
# ==============================
print("📊 Calculating similarity matrix...")
cosine_scores = util.cos_sim(embeddings, embeddings)

# ==============================
# DETECT DUPLICATES
# ==============================
print("🔎 Detecting duplicates...")

visited = set()
duplicate_groups = []

for i in range(len(texts)):
    if i in visited:
        continue

    group = [i]

    for j in range(i + 1, len(texts)):
        if cosine_scores[i][j] >= SIMILARITY_THRESHOLD:
            group.append(j)
            visited.add(j)

    if len(group) > 1:
        duplicate_groups.append(group)

print(f"✅ Duplicate groups found: {len(duplicate_groups)}")

# ==============================
# FORMAT OUTPUT
# ==============================
duplicates_output = []

for group in duplicate_groups:
    group_data = []
    for idx in group:
        group_data.append({
            "id": requirements[idx]["id"],
            "text": requirements[idx]["text"]
        })
    duplicates_output.append(group_data)

output = {
    "summary": {
        "total_requirements": len(requirements),
        "duplicate_groups": len(duplicate_groups),
        "similarity_threshold": SIMILARITY_THRESHOLD
    },
    "duplicates": duplicates_output
}

# ==============================
# SAVE REPORT
# ==============================
with open("duplicate_report.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=4, ensure_ascii=False)

print("📁 duplicate_report.json generated successfully!")
print("🚀 Duplicate detection completed.")