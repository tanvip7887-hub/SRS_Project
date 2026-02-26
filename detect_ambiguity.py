import json
import re
import spacy

# =========================
# CONFIGURATION
# =========================

# Strong vague words (kept limited to avoid over-detection)
VAGUE_WORDS = [
    "fast", "quick", "efficient",
    "optimal", "appropriate",
    "robust", "sufficient",
    "adequate", "minimal",
    "etc", "and so on"
]

# Weak modal verbs (strong ambiguity indicators)
WEAK_MODALS = ["may", "might", "should"]

# Time expressions (ambiguous timing)
TIME_WORDS = ["soon", "later", "immediately", "frequently", "periodically"]

# Quantity expressions
QUANTITY_WORDS = ["several", "some", "many", "few", "most", "enough"]

# Vague verbs (ONLY strong vague verbs)
VAGUE_VERBS = ["handle", "process", "manage"]

# Performance metrics requiring numeric values
PERFORMANCE_PATTERNS = [
    r"response time",
    r"load time",
    r"throughput",
    r"latency"
]

# =========================
# LOAD REQUIREMENTS
# =========================

print("🟢 Loading requirements...")

with open("requirements.json", "r", encoding="utf-8") as f:
    requirements = json.load(f)

# Convert dictionary to list format
if isinstance(requirements, dict):
    requirements = [{"id": key, "text": value} for key, value in requirements.items()]

print(f"Total requirements: {len(requirements)}")

# =========================
# NLP SETUP
# =========================

print("🟢 Loading spaCy model...")
nlp = spacy.load("en_core_web_sm")

# =========================
# HELPER FUNCTIONS
# =========================

def is_missing_measurement(text):
    """
    Detect performance requirements that mention metrics
    but do not include numeric values.
    """
    for pattern in PERFORMANCE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            if not re.search(r"\d+", text):
                return True
    return False


def contains_multiple_shall(text):
    """
    Detect multiple actions by counting SHALL occurrences.
    """
    return text.lower().count(" shall ") > 1


# =========================
# AMBIGUITY DETECTION
# =========================

def detect_ambiguity(text):
    text_lower = text.lower()
    ambiguous_flags = set()
    word_count = len(text.split())

    # 1️⃣ Weak Modals (Strong signal)
    for modal in WEAK_MODALS:
        if re.search(r"\b" + modal + r"\b", text_lower):
            ambiguous_flags.add(f"weak_modal:{modal}")

    # 2️⃣ Vague Words
    for word in VAGUE_WORDS:
        if word in text_lower:
            ambiguous_flags.add(f"vague_word:{word}")

    # 3️⃣ Time Expressions
    for word in TIME_WORDS:
        if re.search(r"\b" + word + r"\b", text_lower):
            ambiguous_flags.add(f"time_expression:{word}")

    # 4️⃣ Quantity Expressions
    for word in QUANTITY_WORDS:
        if re.search(r"\b" + word + r"\b", text_lower):
            ambiguous_flags.add(f"quantity_expression:{word}")

    # 5️⃣ Missing Measurement for Performance
    if is_missing_measurement(text):
        ambiguous_flags.add("missing_measurement")

    # 6️⃣ Multiple Actions (Only if multiple SHALL)
    if contains_multiple_shall(text):
        ambiguous_flags.add("multiple_actions")

    # 7️⃣ Contextual Vague Verb Detection
    # Only flag if short requirement (less specific)
    for verb in VAGUE_VERBS:
        if re.search(r"\b" + verb + r"\b", text_lower):
            if word_count < 15:
                ambiguous_flags.add(f"vague_verb:{verb}")

    # 8️⃣ Too Short Requirement
    if word_count < 5:
        ambiguous_flags.add("too_short")

    # =========================
    # Ambiguity Score (Balanced)
    # =========================
    score = min(len(ambiguous_flags) / 3, 1.0)

    return list(ambiguous_flags), round(score, 2)


# =========================
# PROCESS REQUIREMENTS
# =========================

ambiguous_results = []
clear_count = 0

for req in requirements:
    flags, score = detect_ambiguity(req["text"])

    if flags:
        ambiguous_results.append({
            "id": req["id"],
            "text": req["text"],
            "ambiguous_flags": flags,
            "ambiguity_score": score
        })
    else:
        clear_count += 1

# =========================
# SAVE OUTPUT
# =========================

with open("ambiguity_report.json", "w", encoding="utf-8") as f:
    json.dump(ambiguous_results, f, indent=4)

# =========================
# SUMMARY
# =========================

ambiguous_count = len(ambiguous_results)

print("\n✅ Ambiguity detection complete!")
print("📄 Saved as ambiguity_report.json")

print("\n📊 SUMMARY")
print(f"Total requirements: {len(requirements)}")
print(f"Ambiguous: {ambiguous_count}")
print(f"Clear: {clear_count}")