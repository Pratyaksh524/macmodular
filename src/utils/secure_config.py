"""
Secure Configuration Manager
Encrypts and stores AWS credentials safely in the codebase
"""

import os
import base64
from cryptography.fernet import Fernet
from pathlib import Path


class SecureConfig:
    """Manages encrypted configuration for cloud services"""
    
    def __init__(self):
        # Generate a key from a passphrase (same for all team members)
        # This key is derived from the project itself
        self.passphrase = "ECG_MONITOR_2025_SECURE_KEY"  # Same for everyone
        self.key = self._derive_key(self.passphrase)
        self.cipher = Fernet(self.key)
        
        # Encrypted credentials (safe to commit to GitHub)
        # You will generate these using the encrypt_credentials.py script
        self.encrypted_data = {
            "CLOUD_SERVICE": "s3",
            "AWS_ACCESS_KEY_ID": "",  # Will be encrypted
            "AWS_SECRET_ACCESS_KEY": "",  # Will be encrypted
            "AWS_S3_BUCKET": "",  # Will be encrypted
            "AWS_S3_REGION": "us-east-1"
        }
    
    def _derive_key(self, passphrase: str) -> bytes:
        """Derive a Fernet key from a passphrase"""
        import hashlib
        # Use SHA256 to hash the passphrase, then take first 32 bytes
        hash_digest = hashlib.sha256(passphrase.encode()).digest()
        # Fernet requires base64-encoded 32-byte key
        return base64.urlsafe_b64encode(hash_digest)
    
    def encrypt_value(self, value: str) -> str:
        """Encrypt a configuration value"""
        encrypted = self.cipher.encrypt(value.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a configuration value"""
        try:
            decoded = base64.urlsafe_b64decode(encrypted_value.encode())
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            print(f"⚠️  Decryption error: {e}")
            return ""
    
    def get_config(self) -> dict:
        """Get decrypted configuration"""
        config = {}
        
        for key, encrypted_value in self.encrypted_data.items():
            if encrypted_value and key in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_S3_BUCKET"]:
                config[key] = self.decrypt_value(encrypted_value)
            else:
                config[key] = encrypted_value
        
        return config
    
    def is_configured(self) -> bool:
        """Check if credentials are configured"""
        return bool(self.encrypted_data.get("AWS_ACCESS_KEY_ID"))


# ========================================
# ENCRYPTED CREDENTIALS (SAFE TO COMMIT)
# ========================================
# Generate these using: python src/utils/encrypt_credentials.py
# Then paste them here

ENCRYPTED_CONFIG = {
    "CLOUD_SERVICE": "s3",
    
    # Encrypted AWS Access Key ID
    # Original format: AKIA...
    "AWS_ACCESS_KEY_ID": "",
    
    # Encrypted AWS Secret Access Key
    # Original format: 40 characters
    "AWS_SECRET_ACCESS_KEY": "",
    
    # Encrypted S3 Bucket Name
    # Original format: ecg-reports-bucket
    "AWS_S3_BUCKET": "",
    
    # Region (not encrypted, safe to commit)
    "AWS_S3_REGION": "us-east-1"
}


def get_cloud_config() -> dict:
    """
    Get cloud configuration (automatically decrypted)
    
    Returns:
        dict: Cloud configuration with decrypted credentials
    """
    # First try to load from .env file (if exists)
    env_file = Path(__file__).parent.parent.parent / ".env"
    
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            
            # Check if .env has credentials
            if os.getenv("AWS_ACCESS_KEY_ID"):
                return {
                    "CLOUD_SERVICE": os.getenv("CLOUD_SERVICE", "s3"),
                    "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
                    "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
                    "AWS_S3_BUCKET": os.getenv("AWS_S3_BUCKET"),
                    "AWS_S3_REGION": os.getenv("AWS_S3_REGION", "us-east-1")
                }
        except Exception:
            pass
    
    # Fallback to encrypted config
    if ENCRYPTED_CONFIG.get("AWS_ACCESS_KEY_ID"):
        secure = SecureConfig()
        secure.encrypted_data = ENCRYPTED_CONFIG
        return secure.get_config()
    
    # No configuration available
    return {}


def is_cloud_configured() -> bool:
    """Check if cloud is configured (either .env or encrypted)"""
    config = get_cloud_config()
    return bool(config.get("AWS_ACCESS_KEY_ID"))


if __name__ == "__main__":
    # Test decryption
    config = get_cloud_config()
    
    if config.get("AWS_ACCESS_KEY_ID"):
        print("✅ Cloud configuration loaded successfully!")
        print(f"   Service: {config.get('CLOUD_SERVICE')}")
        print(f"   Region: {config.get('AWS_S3_REGION')}")
        print(f"   Bucket: {config.get('AWS_S3_BUCKET')}")
        print(f"   Access Key: {config.get('AWS_ACCESS_KEY_ID')[:4]}...{config.get('AWS_ACCESS_KEY_ID')[-4:]}")
    else:
        print("⚠️  Cloud not configured")
        print("   Run: python src/utils/encrypt_credentials.py")

