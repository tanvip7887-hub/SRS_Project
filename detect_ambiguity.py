import json
import re

# =========================
# CONFIGURATION
# =========================

VAGUE_WORDS = [
    "fast", "quick", "efficient", "user-friendly",
    "optimal", "appropriate", "robust", "secure",
    "flexible", "easy", "simple", "quickly",
    "as soon as possible", "high performance",
    "sufficient", "adequate", "minimal",
    "etc", "and so on"
]

WEAK_MODALS = ["may", "might", "should"]

# =========================
# LOAD REQUIREMENTS
# =========================

print("🟢 Loading requirements...")

with open("requirements.json", "r", encoding="utf-8") as f:
    requirements = json.load(f)

if isinstance(requirements, dict):
    requirements = [
        {"id": key, "text": value}
        for key, value in requirements.items()
    ]

print(f"Total requirements: {len(requirements)}")

results = []

# =========================
# AMBIGUITY CHECK FUNCTION
# =========================

def is_ambiguous(text):
    text_lower = text.lower()

    # Check vague words
    for word in VAGUE_WORDS:
        if word in text_lower:
            return True

    # Check weak modal verbs
    for modal in WEAK_MODALS:
        if re.search(r"\b" + modal + r"\b", text_lower):
            return True

    # Too short (underspecified requirement)
    if len(text.split()) < 5:
        return True

    return False

# =========================
# PROCESS REQUIREMENTS
# =========================

for req in requirements:
    status = "AMBIGUOUS" if is_ambiguous(req["text"]) else "CLEAR"

    results.append({
        "id": req["id"],
        "text": req["text"],
        "status": status
    })

# =========================
# SAVE OUTPUT
# =========================

with open("ambiguity_report.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4)

# =========================
# SUMMARY
# =========================

ambiguous_count = sum(1 for r in results if r["status"] == "AMBIGUOUS")
clear_count = sum(1 for r in results if r["status"] == "CLEAR")

print("\n✅ Ambiguity detection complete!")
print("📄 Saved as ambiguity_report.json")

print("\n📊 SUMMARY")
print(f"Total: {len(results)}")
print(f"AMBIGUOUS: {ambiguous_count}")
print(f"CLEAR: {clear_count}")