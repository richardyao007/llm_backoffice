# ingest/embedding.py

import requests
from config import EMBEDDING_PROVIDER, OLLAMA_BASE_URL, OLLAMA_EMBED_MODEL, HF_EMBED_MODEL

def embed_with_ollama(texts):
    vectors = []
    for t in texts:
        r = requests.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={
                "model": OLLAMA_EMBED_MODEL,
                "prompt": t
            },
            timeout=60
        )
        vectors.append(r.json()["embedding"])
    return vectors


def embed_with_huggingface(texts):
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(HF_EMBED_MODEL)
    return model.encode(texts).tolist()


def embed(texts):
    if EMBEDDING_PROVIDER == "ollama":
        return embed_with_ollama(texts)
    elif EMBEDDING_PROVIDER == "huggingface":
        return embed_with_huggingface(texts)
    else:
        raise ValueError("Unknown embedding provider")
