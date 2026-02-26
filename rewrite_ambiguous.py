import json
import time
import re
from openai import OpenAI

# ============================================
# CONNECT TO LM STUDIO
# ============================================
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

BATCH_SIZE = 8
RETRY_DELAY = 2

print("🟢 Loading ambiguous items...")

with open("ambiguity_report.json", "r", encoding="utf-8") as f:
    amb_data = json.load(f)

if isinstance(amb_data, list):
    ambiguous_items = amb_data
else:
    ambiguous_items = [{"id": k, "text": v} for k, v in amb_data.items()]

total = len(ambiguous_items)
print("Total ambiguous requirements:", total)

output = []

# ============================================
# CLEANUP & VALIDATION
# ============================================

def enforce_shall(text):
    """
    Ensure rewritten requirement starts with 'The system SHALL'
    """
    text = text.strip()

    if not text.lower().startswith("the system shall"):
        # Remove leading verbs if present
        text = re.sub(r"^(the system|system)\s+", "", text, flags=re.IGNORECASE)
        text = "The system SHALL " + text.lstrip()

    return text


def clean_sentence(text):
    """
    Ensure one sentence only.
    """
    text = text.strip()
    sentences = re.split(r'[.!?]', text)
    return sentences[0].strip() + "."


# ============================================
# TEMPLATE-BASED FALLBACK
# ============================================

def template_rewrite(text):
    replacements = {
        r"\bfast\b": "response time shall be less than 2 seconds",
        r"\bquick\b": "response time shall be less than 2 seconds",
        r"\befficient\b": "resource usage shall be optimized",
        r"\buser-friendly\b": "the interface shall be easy to use",
        r"\bsecure\b": "the system shall comply with security standards",
        r"\bflexible\b": "the system shall support multiple configurations",
        r"\bsimple\b": "the system shall be easy to operate",
    }

    rewritten = text

    for pattern, repl in replacements.items():
        rewritten = re.sub(pattern, repl, rewritten, flags=re.IGNORECASE)

    rewritten = enforce_shall(rewritten)
    rewritten = clean_sentence(rewritten)

    return rewritten


# ============================================
# STRICT LLM REWRITE
# ============================================

def rewrite_batch(batch):
    text_block = "\n\n".join([f"[{item['id']}]\n{item['text']}" for item in batch])

    prompt = f"""
You are a senior Software Requirements Engineering expert.

Rewrite each requirement to be:
- Clear
- Atomic (only ONE action)
- Testable
- Written using "The system SHALL ..."
- Without vague terms
- Without explanation
- ONE sentence only

STRICT OUTPUT FORMAT:
[FR-23] The system SHALL ...
[FR-24] The system SHALL ...

Do not add explanations.
Do not repeat the original.
Keep original meaning.

Rewrite:

{text_block}
"""

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="qwen2.5-coder-1.5b-instruct",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.05,  # lower = more deterministic
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ LLM attempt {attempt+1} failed: {e}")
            time.sleep(RETRY_DELAY)

    print("⚠️ Using template fallback")
    return "\n".join([f"[{item['id']}] {template_rewrite(item['text'])}" for item in batch])


# ============================================
# PARSER
# ============================================

def parse_output(raw_output, batch):
    lines = raw_output.split("\n")
    parsed = {}
    batch_ids = [item["id"] for item in batch]

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("[") and "]" in line:
            req_id = line.split("]")[0].replace("[", "").strip()
            rewritten = line.split("]", 1)[1].strip()

            if req_id in batch_ids:
                rewritten = enforce_shall(rewritten)
                rewritten = clean_sentence(rewritten)
                parsed[req_id] = rewritten

    # Guarantee all IDs exist
    for item in batch:
        if item["id"] not in parsed:
            fallback = template_rewrite(item["text"])
            parsed[item["id"]] = fallback + "  # fallback"

    return parsed


# ============================================
# PROCESS BATCHES
# ============================================

print("🔄 Rewriting started...")

for i in range(0, total, BATCH_SIZE):
    batch = ambiguous_items[i:i+BATCH_SIZE]
    print(f"Processing batch {i//BATCH_SIZE + 1} / {((total-1)//BATCH_SIZE)+1}")

    raw_output = rewrite_batch(batch)
    parsed = parse_output(raw_output, batch)

    for item in batch:
        output.append({
            "id": item["id"],
            "original": item["text"],
            "rewritten": parsed[item["id"]]
        })

    time.sleep(0.2)

# ============================================
# SAVE OUTPUT
# ============================================

with open("rewritten_ambiguity.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=4, ensure_ascii=False)

print("\n✅ Batch rewriting complete!")
print("📄 Saved as rewritten_ambiguity.json")