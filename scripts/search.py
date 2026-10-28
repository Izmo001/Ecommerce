# scripts/search.py
import os
import sys
import psycopg
from pgvector.psycopg import register_vector
import ollama
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")
EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

def search(query: str, limit: int = 3):
    # 1. Embed the user's query
    response = ollama.embeddings(model=EMBED_MODEL, prompt=query)
    query_vector = response["embedding"]

    # 2. Query the database
    conn = psycopg.connect(DB_URL)
    register_vector(conn)

    with conn.cursor() as cur:
        # <=> is the cosine distance operator in pgvector (smaller is better)
        cur.execute("""
            SELECT name, brand, price_cents, 
                   1 - (embedding <=> %s) AS similarity
            FROM products
            ORDER BY embedding <=> %s
            LIMIT %s
        """, (query_vector, query_vector, limit))

        rows = cur.fetchall()

    conn.close()

    print(f"\n🔍 Search Query: '{query}'\n")
    for name, brand, price, similarity in rows:
        print(f"  [{similarity:.3f}] {brand} {name} - ${price/100:.2f}")

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "shoes for hitting the trails"
    search(query)
    