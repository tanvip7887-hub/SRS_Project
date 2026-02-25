import json

print("🟢 Loading files...")

# =========================
# LOAD REQUIREMENTS
# =========================

with open("requirements.json", "r", encoding="utf-8") as f:
    requirements = json.load(f)

with open("duplicates_grouped.json", "r", encoding="utf-8") as f:
    duplicates_grouped = json.load(f)

print(f"Total requirements before cleaning: {len(requirements)}")

# =========================
# COLLECT DUPLICATE IDs TO REMOVE
# =========================

duplicate_removed_ids = set()

for original_id, duplicate_list in duplicates_grouped.items():
    for dup_id in duplicate_list:
        duplicate_removed_ids.add(dup_id)

print(f"Duplicate IDs to remove: {len(duplicate_removed_ids)}")

# =========================
# REMOVE DUPLICATES
# =========================

clean_requirements = {}

for req_id, text in requirements.items():
    if req_id not in duplicate_removed_ids:
        clean_requirements[req_id] = text

print(f"Total requirements after cleaning: {len(clean_requirements)}")

# =========================
# SAVE CLEAN FILE
# =========================

with open("clean_requirements.json", "w", encoding="utf-8") as f:
    json.dump(clean_requirements, f, indent=4, ensure_ascii=False)

print("\n✅ Duplicates removed successfully!")
print("📄 Saved as clean_requirements.json")