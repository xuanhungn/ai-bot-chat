import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

model = SentenceTransformer("all-MiniLM-L6-v2")

def load_kb(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    questions = list(data.keys())
    answers = list(data.values())

    embeddings = model.encode(questions)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))

    return {
        "questions": questions,
        "answers": answers,
        "index": index
    }

def best_kb_match(user_text, kb):
    query_vec = model.encode([user_text])
    D, I = kb["index"].search(query_vec, 1)

    score = D[0][0]
    idx = I[0][0]

    # càng nhỏ càng giống
    if score < 1.0:
        return kb["answers"][idx], score

    return None, score