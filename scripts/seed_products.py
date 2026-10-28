# scripts/seed_products.py
import os
import psycopg
from pgvector.psycopg import register_vector
import ollama
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")
EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

PRODUCTS = [
    ("Nike Air Max 270", "Nike", "Running", 15000, "Breathable mesh upper with a large Max Air unit in the heel for unrivaled comfort.", "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&q=80"),
    ("Adidas Ultraboost 22", "Adidas", "Running", 19000, "Responsive Boost midsole provides incredible energy return. A Primeknit+ upper adapts to the foot.", "https://images.unsplash.com/photo-1587563871167-1ee9c731aefb?w=800&q=80"),
    ("New Balance 990v5", "New Balance", "Lifestyle", 18500, "Made in the USA. Premium pigskin suede and mesh upper with dual-density foam collar.", "https://images.unsplash.com/photo-1539185441755-769473a23570?w=800&q=80"),
    ("Converse Chuck Taylor All Star", "Converse", "Lifestyle", 5500, "The iconic high-top sneaker. Canvas upper, classic star ankle patch, and a vulcanized rubber sole.", "https://images.unsplash.com/photo-1607522370275-f14206abe5d3?w=800&q=80"),
    ("Vans Old Skool", "Vans", "Skateboarding", 6500, "The classic side-stripe shoe. Durable suede and canvas uppers with re-enforced toe caps.", "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=800&q=80"),
    ("Nike Dunk Low Retro", "Nike", "Lifestyle", 11000, "Created for the hardwood but taken to the streets. Crisp leather upper with a low-cut collar.", "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=800&q=80"),
    ("Hoka One One Clifton 8", "Hoka", "Running", 14000, "A lightweight, maximal cushioning running shoe. Features a compression-molded EVA midsole.", "https://images.unsplash.com/photo-1549468087-bbfa9f5ce0ea?w=800&q=80"),
    ("Salomon Speedcross 5", "Salomon", "Trail", 13000, "Aggressive grip and precise fit. Contagrip TA outsole with deep lugs for maximum traction on trails.", "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=800&q=80"),
    ("Jordan 1 Retro High OG", "Jordan", "Basketball", 18000, "The shoe that started it all. Encapsulated Air-Sole unit, premium leather, and the iconic Wings logo.", "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?w=800&q=80"),
    ("Asics Gel-Kayano 28", "Asics", "Running", 16000, "Designed for stability and support. FF Blast cushioning for a softer landing.", "https://images.unsplash.com/photo-1584735175315-9d5df23860e6?w=800&q=80"),
    ("Puma Suede Classic", "Puma", "Lifestyle", 7000, "A timeless classic. Rich suede upper with a comfortable sockliner and a thick rubber outsole.", "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=800&q=80"),
    ("Reebok Club C 85", "Reebok", "Lifestyle", 7500, "Clean, minimalist, and timeless. Soft garment leather upper and a low-cut design.", "https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=800&q=80"),
]

def get_embedding(text: str) -> list[float]:
    print(f"Embedding: {text[:50]}...")
    response = ollama.embeddings(model=EMBED_MODEL, prompt=text)
    return response["embedding"]

def main():
    conn = psycopg.connect(DB_URL)
    register_vector(conn)

    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("""
            DROP TABLE IF EXISTS products;
            CREATE TABLE products (
                id BIGSERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                brand TEXT NOT NULL,
                category TEXT NOT NULL,
                price_cents INTEGER NOT NULL,
                description TEXT NOT NULL,
                image_url TEXT NOT NULL,
                embedding vector(768) NOT NULL
            );
        """)

        for name, brand, category, price, desc, img in PRODUCTS:
            text_to_embed = f"{name} by {brand}. {desc}"
            vector = get_embedding(text_to_embed)
            
            cur.execute(
                """INSERT INTO products (name, brand, category, price_cents, description, image_url, embedding) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (name, brand, category, price, desc, img, vector),
            )

    conn.commit()
    conn.close()
    print(f"✅ Successfully seeded {len(PRODUCTS)} shoes.")

if __name__ == "__main__":
    main()