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

# Convert requirements list to dict if needed
if isinstance(requirements, list):
    requirements = {item["id"]: item["text"] for item in requirements}

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
# (ambiguity_report.json contains only ambiguous)
# =========================

ambiguous_requirements = []

for item in ambiguity_data:
    req_id = item["id"]

    # Skip duplicates
    if req_id in duplicate_removed_ids:
        continue

    ambiguous_requirements.append({
        "id": req_id,
        "text": item["text"],
        "ambiguous_flags": item.get("ambiguous_flags", []),
        "ambiguity_score": item.get("ambiguity_score", 0)
    })

# Optional: sort ambiguous requirements by score descending
ambiguous_requirements.sort(key=lambda x: x["ambiguity_score"], reverse=True)

# =========================
# GRAMMAR / FORMAT VALIDATION
# =========================

format_issues = []

for req_id, text in requirements.items():

    # Skip duplicates
    if req_id in duplicate_removed_ids:
        continue

    text_lower = text.lower()

    # Check if SHALL or SHOULD exists
    if "shall" not in text_lower and "should" not in text_lower:
        format_issues.append({
            "id": req_id,
            "text": text,
            "reason": "Missing SHALL/SHOULD keyword"
        })

# =========================
# BUILD ANNOTATED REPORT
# =========================

annotated_srs = {
    "summary": {
        "total_requirements": len(requirements),
        "duplicate_groups": len(duplicates_grouped),
        "duplicates_removed": len(duplicate_removed_ids),
        "ambiguous_count": len(ambiguous_requirements),
        "format_issue_count": len(format_issues)
    },
    "duplicates": duplicate_pairs,
    "ambiguous_requirements": ambiguous_requirements,
    "format_issues": format_issues
}

# =========================
# SAVE OUTPUT
# =========================

with open("annotated_srs.json", "w", encoding="utf-8") as f:
    json.dump(annotated_srs, f, indent=4)

# =========================
# SUMMARY OUTPUT
# =========================

print("\n✅ Quality Issue Report Generated!")
print("📄 Saved as annotated_srs.json")

print("\n📊 SUMMARY")
print(f"Total requirements: {len(requirements)}")
print(f"Duplicate groups: {len(duplicates_grouped)}")
print(f"Duplicates removed: {len(duplicate_removed_ids)}")
print(f"Ambiguous (non-duplicate): {len(ambiguous_requirements)}")
print(f"Format issues (Missing SHALL/SHOULD): {len(format_issues)}")