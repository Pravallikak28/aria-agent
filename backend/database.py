import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(override=True)

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def setup_database():
    """Create tokens table if it doesn't exist"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS google_tokens (
            id SERIAL PRIMARY KEY,
            service VARCHAR(50) UNIQUE NOT NULL,
            token_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database setup complete!")

def save_token(service: str, token_data: str):
    """Save or update token for a service"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO google_tokens (service, token_data, updated_at)
        VALUES (%s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (service)
        DO UPDATE SET token_data = %s, updated_at = CURRENT_TIMESTAMP
    """, (service, token_data, token_data))
    conn.commit()
    cur.close()
    conn.close()

def load_token(service: str):
    """Load token for a service"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT token_data FROM google_tokens WHERE service = %s", (service,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else None

def token_exists(service: str) -> bool:
    """Check if token exists for a service"""
    return load_token(service) is not None