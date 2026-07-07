import json
import os
import re
import unicodedata
from difflib import SequenceMatcher

KB_MIN_SCORE = float(os.getenv("KB_MIN_RATIO", "0.45"))


def load_kb(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    questions = list(data.keys())
    answers = list(data.values())
    normalized = [_normalize_text(q) for q in questions]

    return {"questions": questions, "answers": answers, "normalized": normalized}


def _normalize_text(text):
    text = unicodedata.normalize("NFKC", text).lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def _token_jaccard(a, b):
    sa = set(a.split())
    sb = set(b.split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def best_kb_match(user_text, kb):
    query = _normalize_text(user_text)
    if not query:
        return None, 0.0

    best_idx = -1
    best_score = 0.0

    for idx, item in enumerate(kb["normalized"]):
        seq_score = SequenceMatcher(None, query, item).ratio()
        token_score = _token_jaccard(query, item)
        score = 0.6 * seq_score + 0.4 * token_score
        if score > best_score:
            best_score = score
            best_idx = idx

    threshold = KB_MIN_SCORE if 0.0 <= KB_MIN_SCORE <= 1.0 else 0.45
    if best_idx >= 0 and best_score >= threshold:
        return kb["answers"][best_idx], best_score

    return None, best_score
