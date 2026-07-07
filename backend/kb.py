import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

model = SentenceTransformer("all-MiniLM-L6-v2")
KB_MIN_SCORE = float(os.getenv("KB_MIN_RATIO", "1.0"))


def load_kb(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    questions = list(data.keys())
    answers = list(data.values())
    embeddings = model.encode(questions)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings, dtype=np.float32))

    return {"questions": questions, "answers": answers, "index": index}


def best_kb_match(user_text, kb):
    query_vec = model.encode([user_text])
    D, I = kb["index"].search(np.array(query_vec, dtype=np.float32), 1)

    score = float(D[0][0])
    idx = int(I[0][0])

    if score < KB_MIN_SCORE:
        return kb["answers"][idx], score

    return None, score
