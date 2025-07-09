# utils/encryption.py

from cryptography.fernet import Fernet
import os

# Load key from environment variable or generate a fallback key (not recommended for production)
key = os.getenv('ENCRYPTION_KEY')

if not key:
    print("⚠️  ENCRYPTION_KEY not found in environment. Generating temporary key.")
    key = Fernet.generate_key().decode()

fernet = Fernet(key.encode())

def encrypt_data(plaintext: str) -> str:
    """Encrypt plain text data and return a token string."""
    if not plaintext:
        return ""
    return fernet.encrypt(plaintext.encode()).decode()

def decrypt_data(token: str) -> str:
    """Decrypt token string and return plain text."""
    if not token:
        return ""
    return fernet.decrypt(token.encode()).decode()
