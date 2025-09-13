#!/usr/bin/env python3

"""
Generate a secure Django secret key for production use
"""

import secrets
import string

def generate_secret_key(length=64):
    """Generate a cryptographically secure secret key."""
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(alphabet) for _ in range(length))

if __name__ == "__main__":
    secret_key = generate_secret_key()
    print("🔐 Generated secure Django SECRET_KEY:")
    print(f"SECRET_KEY={secret_key}")
    print("\n⚠️  Save this key securely and use it in your .env.production file!")
    print("⚠️  Never commit this key to version control!")