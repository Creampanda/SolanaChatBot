import os

# Set up environment variables for application configuration

# Default port is 8000 unless specified in the environment
PORT = int(os.environ.get("PORT", 8000))

# Default PostgreSQL username is "admin" unless specified in the environment
POSTGRES_USER = os.environ.get("POSTGRES_USER", "admin")

# Default PostgreSQL password is "admin" unless specified in the environment
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "admin")

# Default PostgreSQL database name is "postgres" unless specified in the environment
POSTGRES_DB = os.environ.get("POSTGRES_DB", "postgres")

# Solana RPC URL should be specified in the environment
SOLANA_RPC_URL = os.environ.get("SOLANA_RPC_URL")
