import os

PORT = int(os.environ.get("PORT", 8000))
POSTGRES_USER = os.environ.get("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "admin")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "postgres")
SOLANA_RPC_URL = os.environ.get("SOLANA_RPC_URL")
