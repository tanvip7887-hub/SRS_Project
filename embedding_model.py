from sentence_transformers import SentenceTransformer

MODEL_PATH = r"D:\SRS_Analyzer\models\models--sentence-transformers--all-mpnet-base-v2\snapshots\e8c3b32edf5434bc2275fc9bab85f82640a19130"

print("🟢 Loading MPNet from local project folder...")

MODEL = SentenceTransformer(MODEL_PATH)

print("✅ Model loaded successfully!")

def get_embeddings(texts):
    return MODEL.encode(texts, convert_to_tensor=True)