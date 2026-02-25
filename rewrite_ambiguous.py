import json
import time
from openai import OpenAI

# ============================================
# CONNECT TO LM STUDIO
# ============================================
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

BATCH_SIZE = 10

print("🟢 Loading ambiguous items...")

with open("ambiguity_report.json", "r", encoding="utf-8") as f:
    amb_data = json.load(f)

# Normalize input format
if isinstance(amb_data, list):
    ambiguous_items = amb_data
else:
    ambiguous_items = [{"id": k, "text": v} for k, v in amb_data.items()]

total = len(ambiguous_items)
print("Total ambiguous requirements:", total)

output = []

# ============================================
# STRICT REWRITE FUNCTION (forces bracket format)
# ============================================

def rewrite_batch(batch):
    text_block = "\n\n".join(
        [f"[{item['id']}]\n{item['text']}" for item in batch]
    )

    prompt = f"""
Rewrite each software requirement clearly and unambiguously using **shall**.

STRICT RULES:
1. Output MUST be EXACTLY in this format:
   [FR-23] rewritten requirement
   [FR-24] rewritten requirement
2. ID MUST be inside square brackets.
3. ONE sentence per requirement.
4. NO bullets, NO numbering, NO explanation.
5. Keep the meaning the same.
6. Do not repeat the original.

Rewrite the following requirements:

{text_block}
"""

    response = client.chat.completions.create(
        model="qwen2.5-coder-1.5b-instruct",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
        temperature=0.1,
    )

    return response.choices[0].message.content.strip()


# ============================================
# STRONG FLEXIBLE PARSER
# ============================================

def parse_output(raw_output, batch):
    lines = raw_output.split("\n")
    parsed = {}

    batch_ids = [item["id"] for item in batch]

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Format 1 — [FR-23] text
        if line.startswith("[") and "]" in line:
            req_id = line.split("]")[0].replace("[", "").strip()
            rewritten = line.split("]", 1)[1].strip()
            if req_id in batch_ids:
                parsed[req_id] = rewritten
            continue

        # Format 2 — FR-23: text
        if ":" in line:
            possible_id = line.split(":", 1)[0].strip()
            if possible_id in batch_ids:
                rewritten = line.split(":", 1)[1].strip()
                parsed[possible_id] = rewritten
                continue

        # Format 3 — FR-23 text
        for item in batch:
            if line.startswith(item["id"]):
                rewritten = line.replace(item["id"], "", 1).strip(" :-")
                parsed[item["id"]] = rewritten
                break

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
        req_id = item["id"]
        original = item["text"]
        rewritten = parsed.get(req_id, "REWRITE_FAILED")

        output.append({
            "id": req_id,
            "original": original,
            "rewritten": rewritten
        })

    time.sleep(0.2)

# ============================================
# SAVE OUTPUT
# ============================================

with open("rewritten_ambiguity.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=4, ensure_ascii=False)

print("\n✅ Batch rewriting complete!")
print("📄 Saved as rewritten_ambiguity.json")