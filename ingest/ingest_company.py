# ingest/ingest_company.py

import os
import sys
from qdrant_client import QdrantClient
from embedding import embed

COMPANY_ID = "company_a"
DATA_DIR = f"data/{COMPANY_ID}"
COLLECTION = f"{COMPANY_ID}_backoffice"

def load_documents(data_dir):
    docs = []
    for root, _, files in os.walk(data_dir):
        for f in files:
            path = os.path.join(root, f)
            if not f.endswith(".txt"):
                continue
            with open(path, "r", encoding="utf-8") as fp:
                content = fp.read().strip()
                if content:
                    docs.append({
                        "text": content,
                        "category": os.path.basename(root)
                    })

    return docs

def main():
    print("== RAG INGEST START ==")
    print(f"Company      : {COMPANY_ID}")
    print(f"Data dir     : {DATA_DIR}")
    print(f"Collection  : {COLLECTION}")

    print("→ Loading documents")
    documents = load_documents(DATA_DIR)
    print(f"  loaded {len(documents)} documents")

    if not documents:
        raise RuntimeError("No documents loaded")

    print("→ Embedding documents")
    texts = [d["text"] for d in documents]
    vectors = embed(texts)

    client = QdrantClient(url="http://localhost:6333")

    client.recreate_collection(
        collection_name=COLLECTION,
        vectors_config={
            "size": len(vectors[0]),
            "distance": "Cosine",
        },
    )

    client.upload_collection(
        collection_name=COLLECTION,
        vectors=vectors,
        payload = [
            {
                "company": COMPANY_ID,
                "category": d["category"],
                "text": d["text"]
            }
            for d in documents
        ],
    )

    print("== RAG INGEST DONE ==")

if __name__ == "__main__":
    sys.exit(main())
