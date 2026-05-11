import hashlib
import os


def hash_api_key(plaintext: str) -> str:
    pepper = os.getenv("API_KEY_PEPPER", "dev_pepper_change_me")
    return hashlib.sha256(f"{pepper}:{plaintext}".encode("utf-8")).hexdigest()
