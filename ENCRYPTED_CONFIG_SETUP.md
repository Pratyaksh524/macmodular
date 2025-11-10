# 🔐 Encrypted Cloud Configuration

## 🎯 No Separate .env File Needed!

This approach encrypts your AWS credentials **directly in the codebase** so teammates can `git pull` and immediately have cloud access - **NO separate credential sharing needed!**

---

## ✅ Benefits

- ✅ **One-time setup** - Encrypt credentials once, commit to GitHub
- ✅ **Zero teammate setup** - They just `git pull` and it works
- ✅ **Secure** - Credentials are encrypted, not plaintext
- ✅ **No .env management** - No copying files, no credential sharing
- ✅ **Automatic decryption** - App automatically decrypts on startup
- ✅ **Fallback support** - Still supports .env for local dev

---

## 🚀 Setup (One-Time - By Divyansh)

### Step 1: Install Cryptography Package

```bash
pip install cryptography
```

### Step 2: Encrypt Your Credentials

```bash
cd /Users/deckmount/Downloads/modularecg-main
python src/utils/encrypt_credentials.py
```

**You'll be prompted for:**
```
AWS_ACCESS_KEY_ID: AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_S3_BUCKET: ecg-reports-bucket
AWS_S3_REGION: us-east-1
```

### Step 3: Copy Encrypted Output

The script will output something like:

```python
ENCRYPTED_CONFIG = {
    "CLOUD_SERVICE": "s3",
    "AWS_ACCESS_KEY_ID": "gAAAAABl...(encrypted)...==",
    "AWS_SECRET_ACCESS_KEY": "gAAAAABl...(encrypted)...==",
    "AWS_S3_BUCKET": "gAAAAABl...(encrypted)...==",
    "AWS_S3_REGION": "us-east-1"
}
```

### Step 4: Update secure_config.py

Open `src/utils/secure_config.py` and **replace** the empty `ENCRYPTED_CONFIG` with your encrypted one.

**Before:**
```python
ENCRYPTED_CONFIG = {
    "CLOUD_SERVICE": "s3",
    "AWS_ACCESS_KEY_ID": "",  # Empty
    "AWS_SECRET_ACCESS_KEY": "",  # Empty
    "AWS_S3_BUCKET": "",  # Empty
    "AWS_S3_REGION": "us-east-1"
}
```

**After:**
```python
ENCRYPTED_CONFIG = {
    "CLOUD_SERVICE": "s3",
    "AWS_ACCESS_KEY_ID": "gAAAAABl...(your encrypted key)...==",
    "AWS_SECRET_ACCESS_KEY": "gAAAAABl...(your encrypted secret)...==",
    "AWS_S3_BUCKET": "gAAAAABl...(your encrypted bucket)...==",
    "AWS_S3_REGION": "us-east-1"
}
```

### Step 5: Test Decryption

```bash
python src/utils/secure_config.py
```

**Expected output:**
```
✅ Cloud configuration loaded successfully!
   Service: s3
   Region: us-east-1
   Bucket: ecg-reports-bucket
   Access Key: AKIA...MPLE
```

### Step 6: Commit and Push

```bash
git add src/utils/secure_config.py
git add src/utils/encrypt_credentials.py
git add src/utils/cloud_uploader.py
git add requirements.txt
git commit -m "Add encrypted cloud configuration"
git push
```

---

## 👥 For Teammates (PTR, Indresh)

### Their Setup (2 Minutes - EASY!)

```bash
# 1. Pull latest code
git pull

# 2. Install dependencies (includes cryptography)
pip install -r requirements.txt

# 3. Run the app
python src/main.py

# ✅ CLOUD UPLOAD WORKS AUTOMATICALLY!
```

**That's it!** No .env file, no credential sharing, no setup!

---

## 🔒 Security

### How It Works

1. **Encryption Key**: Derived from a passphrase in the code
2. **Same Key for All**: All team members use the same decryption key
3. **Encrypted Values**: Only encrypted strings are in GitHub
4. **Auto-Decrypt**: App decrypts on startup using the built-in key

### Is It Secure?

**Comparison:**

| Method | Security Level | Ease of Use |
|--------|---------------|-------------|
| **Plaintext in code** | ❌ INSECURE | ✅ Easy |
| **Encrypted in code** | ⚠️ MODERATE | ✅ Very Easy |
| **.env file** | ✅ SECURE | ⚠️ Manual sharing |
| **Environment variables** | ✅ SECURE | ❌ Complex setup |

**Encrypted config is:**
- ✅ **Better than** plaintext in code
- ✅ **Easier than** managing .env files
- ⚠️ **Less secure than** external secret management (AWS Secrets Manager, HashiCorp Vault)

**Good for:**
- ✅ Small teams (3-5 people)
- ✅ Internal projects
- ✅ Development/staging environments

**Not recommended for:**
- ❌ Public open-source projects
- ❌ Production with strict compliance requirements
- ❌ Large teams with frequent credential rotation

---

## 🔄 How Auto-Decryption Works

```python
# When app starts:
CloudUploader → secure_config.py → Decrypt credentials → Use S3

# Priority:
1. Try encrypted config (built-in)
2. Fallback to .env file (if exists)
3. Fallback to environment variables
```

**Console output:**
```
✅ Using encrypted cloud configuration (built-in)
```

---

## 🆘 Troubleshooting

### Issue: "Module 'cryptography' not found"

**Solution:**
```bash
pip install cryptography
```

---

### Issue: "Decryption error"

**Possible causes:**
1. Wrong passphrase in `secure_config.py`
2. Corrupted encrypted string
3. Encryption/decryption mismatch

**Solution:**
Re-run encryption script and update `secure_config.py`

---

### Issue: "Cloud not configured"

**Solution:**
Check if `ENCRYPTED_CONFIG` in `src/utils/secure_config.py` is filled with encrypted values (not empty strings)

---

## 🔄 Updating Credentials

### If You Need to Change AWS Credentials:

```bash
# 1. Re-run encryption
python src/utils/encrypt_credentials.py

# 2. Copy new encrypted output

# 3. Update src/utils/secure_config.py

# 4. Commit and push
git add src/utils/secure_config.py
git commit -m "Update encrypted cloud credentials"
git push

# 5. Teammates git pull (automatic!)
```

---

## 📊 Comparison: Encrypted vs .env

### With .env File:
```
Divyansh:
  1. Create .env
  2. Add credentials
  3. Share via secure channel

PTR/Indresh:
  1. git pull
  2. Get credentials from Divyansh (WhatsApp)
  3. Create .env
  4. Paste credentials
  5. Test connection
  
Total: 5 steps, manual sharing
```

### With Encrypted Config:
```
Divyansh:
  1. Run encrypt_credentials.py
  2. Update secure_config.py
  3. git push

PTR/Indresh:
  1. git pull
  2. Works immediately!
  
Total: 2 steps, automatic
```

---

## 🎯 Summary

**For You (Divyansh):**
- ✅ Encrypt once
- ✅ Commit to GitHub
- ✅ Done forever!

**For Teammates:**
- ✅ `git pull`
- ✅ Cloud works automatically
- ✅ Zero setup!

**Perfect for small teams who want zero-friction cloud setup!** 🚀

---

## 📝 Files Involved

```
modularecg-main/
├── src/utils/
│   ├── secure_config.py          ← Encrypted credentials here
│   ├── encrypt_credentials.py    ← Tool to encrypt
│   └── cloud_uploader.py         ← Auto-decrypts and uses
├── requirements.txt               ← Added cryptography
└── ENCRYPTED_CONFIG_SETUP.md     ← This guide
```

---

**Last Updated:** November 10, 2025  
**Maintained by:** Divyansh  
**Encryption Method:** Fernet (AES-128)

