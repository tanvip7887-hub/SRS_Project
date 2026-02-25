import json
import requests
import math

print("🟢 Loading files...")

# =========================
# BALANCED SETTINGS (CPU + Accuracy)
# =========================

LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
MODEL_NAME = "mistral-7b-instruct-v0.3"

BATCH_SIZE = 15        # 76 req → ~5 batches (fast + accurate)
TEMPERATURE = 0.1      # stable output
MAX_TOKENS = 700       # enough for 15 rewrites
TIMEOUT = 180

# =========================
# LOAD FILES
# =========================

with open("clean_requirements.json", "r", encoding="utf-8") as f:
    clean_requirements = json.load(f)

with open("ambiguity_report.json", "r", encoding="utf-8") as f:
    ambiguous_list = json.load(f)

ambiguous_dict = {item["id"]: item["text"] for item in ambiguous_list}

print(f"Total clean requirements: {len(clean_requirements)}")
print(f"Ambiguous to rewrite: {len(ambiguous_dict)}")

# =========================
# SAFE JSON EXTRACTION
# =========================

def extract_json(text):
    text = text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except:
        return None

# =========================
# REWRITE FUNCTION
# =========================

def rewrite_batch(batch_dict):

    formatted = "\n".join(
        [f"{req_id}: {text}" for req_id, text in batch_dict.items()]
    )

    prompt = f"""
Rewrite the following ambiguous software requirements.

STRICT RULES:
- Replace SHOULD or MAY with SHALL.
- Remove vague words.
- Make requirements measurable and testable.
- ALWAYS rewrite every requirement.
- Keep SAME requirement ID.
- Return ONLY valid JSON like:
{{ "REQ-ID": "Rewritten text" }}

If you do not rewrite a requirement, it will be considered incorrect.

Requirements:
{formatted}
"""

    response = requests.post(
        LM_STUDIO_URL,
        json={
            "model": MODEL_NAME,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKENS
        },
        timeout=TIMEOUT
    )

    result = response.json()

    if "choices" not in result:
        raise ValueError("Invalid response from model.")

    content = result["choices"][0]["message"]["content"]
    parsed = extract_json(content)

    if not parsed:
        raise ValueError("Model did not return valid JSON.")

    return parsed

# =========================
# PROCESS BATCHES
# =========================

rewritten_requirements = clean_requirements.copy()
ambiguous_items = list(ambiguous_dict.items())

total_batches = math.ceil(len(ambiguous_items) / BATCH_SIZE)

for i in range(total_batches):

    print(f"🚀 Processing batch {i+1}/{total_batches}")

    batch_slice = ambiguous_items[i*BATCH_SIZE : (i+1)*BATCH_SIZE]
    batch_dict = dict(batch_slice)

    try:
        rewritten_batch = rewrite_batch(batch_dict)

        # Case 1: Dictionary format
        if isinstance(rewritten_batch, dict):
            for req_id, new_text in rewritten_batch.items():
                if req_id in batch_dict:
                    rewritten_requirements[req_id] = new_text.strip()

        # Case 2: List format (model variation)
        elif isinstance(rewritten_batch, list):
            for item in rewritten_batch:
                if isinstance(item, dict):
                    req_id = item.get("ID") or item.get("id")
                    new_text = (
                        item.get("text")
                        or item.get("requirement")
                        or item.get("rewritten")
                    )
                    if req_id and new_text and req_id in batch_dict:
                        rewritten_requirements[req_id] = new_text.strip()

    except Exception as e:
        print(f"⚠ Batch {i+1} failed. Keeping originals.")
        print("Reason:", e)

        for req_id in batch_dict:
            rewritten_requirements[req_id] = batch_dict[req_id]

# =========================
# SAVE OUTPUT
# =========================

with open("rewritten_requirements.json", "w", encoding="utf-8") as f:
    json.dump(rewritten_requirements, f, indent=4, ensure_ascii=False)

print("\n✅ Rewriting complete!")
print("📄 Saved as rewritten_requirements.json")