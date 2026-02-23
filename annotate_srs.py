import json

print("🟢 Loading files...")

# =========================
# LOAD FILES
# =========================

with open("requirements.json", "r", encoding="utf-8") as f:
    requirements = json.load(f)

with open("duplicates_grouped.json", "r", encoding="utf-8") as f:
    duplicates_grouped = json.load(f)

with open("ambiguity_report.json", "r", encoding="utf-8") as f:
    ambiguity_data = json.load(f)

# =========================
# PROCESS DUPLICATES
# =========================

duplicate_pairs = []
duplicate_removed_ids = set()

for original_id, dup_list in duplicates_grouped.items():
    for dup_id in dup_list:
        duplicate_pairs.append({
            "req1": original_id,
            "req2": dup_id
        })
        duplicate_removed_ids.add(dup_id)

# =========================
# PROCESS AMBIGUOUS
# (Exclude duplicates)
# =========================

ambiguous_requirements = []

for item in ambiguity_data:
    req_id = item["id"]

    # Skip if it is duplicate (we remove those)
    if req_id in duplicate_removed_ids:
        continue

    if item["status"] == "AMBIGUOUS":
        ambiguous_requirements.append({
            "id": req_id,
            "text": item["text"]
        })

# =========================
# BUILD REPORT
# =========================

annotated_srs = {
    "summary": {
        "total_requirements": len(requirements),
        "duplicate_groups": len(duplicates_grouped),
        "duplicates_removed": len(duplicate_removed_ids),
        "ambiguous_count": len(ambiguous_requirements)
    },
    "duplicates": duplicate_pairs,
    "ambiguous_requirements": ambiguous_requirements
}

# =========================
# SAVE OUTPUT
# =========================

with open("annotated_srs.json", "w", encoding="utf-8") as f:
    json.dump(annotated_srs, f, indent=4)

print("\n✅ Quality Issue Report Generated!")
print("📄 Saved as annotated_srs.json")

print("\n📊 SUMMARY")
print(f"Total requirements: {len(requirements)}")
print(f"Duplicate groups: {len(duplicates_grouped)}")
print(f"Duplicates removed: {len(duplicate_removed_ids)}")
print(f"Ambiguous (non-duplicate): {len(ambiguous_requirements)}")