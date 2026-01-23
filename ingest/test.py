# test.py

from qdrant_client import QdrantClient
from ingest_company import load_documents, COMPANY_ID
from embedding import embed

DATA_DIR = f"data/{COMPANY_ID}"
COLLECTION = f"{COMPANY_ID}_backoffice"

client = QdrantClient(url="http://localhost:6333")

docs = load_documents(DATA_DIR)
texts = [d["text"] for d in docs]
vectors = embed(texts)

query_vector = embed(["請求書番号 12345 支払いはいつですか？"])[0]

results = client.search_points(collection_name=COLLECTION, query_vector=query_vector, limit=3)
for r in results:
    print(r.payload.get("text"))
