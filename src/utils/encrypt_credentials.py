#!/usr/bin/env python3
"""
Credential Encryption Tool
Encrypts AWS credentials so they can be safely committed to GitHub
"""

import base64
import hashlib
from cryptography.fernet import Fernet


def derive_key(passphrase: str) -> bytes:
    """Derive a Fernet key from a passphrase"""
    hash_digest = hashlib.sha256(passphrase.encode()).digest()
    return base64.urlsafe_b64encode(hash_digest)


def encrypt_value(value: str, key: bytes) -> str:
    """Encrypt a value"""
    cipher = Fernet(key)
    encrypted = cipher.encrypt(value.encode())
    return base64.urlsafe_b64encode(encrypted).decode()


def main():
    print("=" * 70)
    print("🔐 AWS CREDENTIALS ENCRYPTION TOOL")
    print("=" * 70)
    print()
    print("This tool encrypts your AWS credentials so they can be")
    print("safely committed to GitHub. Your teammates will automatically")
    print("decrypt them when they run the app - NO SEPARATE .env NEEDED!")
    print()
    print("=" * 70)
    print()
    
    # Use the same passphrase as in secure_config.py
    passphrase = "ECG_MONITOR_2025_SECURE_KEY"
    key = derive_key(passphrase)
    
    print("📝 Enter your AWS credentials:")
    print()
    
    # Get credentials
    access_key = input("AWS_ACCESS_KEY_ID (starts with AKIA): ").strip()
    secret_key = input("AWS_SECRET_ACCESS_KEY (40 characters): ").strip()
    bucket = input("AWS_S3_BUCKET (e.g., ecg-reports-bucket): ").strip()
    region = input("AWS_S3_REGION (default: us-east-1): ").strip() or "us-east-1"
    
    print()
    print("🔒 Encrypting credentials...")
    print()
    
    # Encrypt
    encrypted_access = encrypt_value(access_key, key)
    encrypted_secret = encrypt_value(secret_key, key)
    encrypted_bucket = encrypt_value(bucket, key)
    
    print("=" * 70)
    print("✅ ENCRYPTED CREDENTIALS (Safe to commit to GitHub)")
    print("=" * 70)
    print()
    print("Copy and paste this into src/utils/secure_config.py")
    print("Replace the ENCRYPTED_CONFIG dictionary:")
    print()
    print("-" * 70)
    print()
    print("ENCRYPTED_CONFIG = {")
    print('    "CLOUD_SERVICE": "s3",')
    print()
    print("    # Encrypted AWS Access Key ID")
    print(f'    "AWS_ACCESS_KEY_ID": "{encrypted_access}",')
    print()
    print("    # Encrypted AWS Secret Access Key")
    print(f'    "AWS_SECRET_ACCESS_KEY": "{encrypted_secret}",')
    print()
    print("    # Encrypted S3 Bucket Name")
    print(f'    "AWS_S3_BUCKET": "{encrypted_bucket}",')
    print()
    print("    # Region (not encrypted)")
    print(f'    "AWS_S3_REGION": "{region}"')
    print("}")
    print()
    print("-" * 70)
    print()
    print("=" * 70)
    print("📋 NEXT STEPS:")
    print("=" * 70)
    print()
    print("1. Copy the ENCRYPTED_CONFIG above")
    print("2. Open: src/utils/secure_config.py")
    print("3. Replace the empty ENCRYPTED_CONFIG with your encrypted one")
    print("4. Save the file")
    print("5. Commit and push to GitHub")
    print()
    print("✅ Your teammates will automatically get cloud access!")
    print("   No .env file needed, no separate credential sharing!")
    print()
    print("=" * 70)
    print()
    
    # Test decryption
    print("🧪 Testing decryption...")
    cipher = Fernet(key)
    
    decoded_access = base64.urlsafe_b64decode(encrypted_access.encode())
    decrypted_access = cipher.decrypt(decoded_access).decode()
    
    if decrypted_access == access_key:
        print("✅ Decryption test PASSED!")
        print(f"   Decrypted: {decrypted_access[:4]}...{decrypted_access[-4:]}")
    else:
        print("❌ Decryption test FAILED!")
    
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

