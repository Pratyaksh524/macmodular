# ☁️ Cloud Upload Setup Guide for Team Members

## 🎯 Goal
Enable cloud sync (AWS S3) on **every device** where the ECG Monitor is installed.

---

## 📋 Prerequisites

Before starting, make sure you have:
- ✅ Python 3.8+ installed
- ✅ Project cloned from GitHub
- ✅ Virtual environment activated
- ✅ All dependencies installed (`pip install -r requirements.txt`)
- ✅ AWS credentials from Divyansh (team lead)

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone <your-repo-url>
cd modularecg-main

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Get AWS Credentials from Team Lead

**Contact Divyansh to get:**
- `AWS_ACCESS_KEY_ID` (e.g., `AKIAIOSFODNN7EXAMPLE`)
- `AWS_SECRET_ACCESS_KEY` (e.g., `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`)
- `AWS_S3_BUCKET` (e.g., `ecg-reports-bucket`)
- `AWS_S3_REGION` (e.g., `us-east-1`)

⚠️ **IMPORTANT:** 
- Share credentials via **secure channels** (encrypted chat, password manager, in person)
- **NEVER** share credentials via email, GitHub issues, or public chat

### Step 3: Create Your `.env` File

```bash
# Copy the template
cp env_template.txt .env

# Edit the file (use any text editor)
nano .env
# OR
code .env  # VS Code
# OR
open .env  # TextEdit on macOS
```

### Step 4: Fill in Your Credentials

Replace the placeholder values in `.env`:

```env
# Before (template):
CLOUD_SERVICE=s3
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_S3_BUCKET=your_bucket_name_here
AWS_S3_REGION=us-east-1

# After (with real credentials):
CLOUD_SERVICE=s3
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_S3_BUCKET=ecg-reports-bucket
AWS_S3_REGION=us-east-1
```

**Save and close the file.**

### Step 5: Test Your Connection

```bash
# Run the test script
python3 test_cloud_connection.py
```

**Expected output:**

```
======================================================================
🔍 ECG MONITOR - CLOUD CONNECTION TEST
======================================================================

Step 1: Checking for .env file...
✅ .env file found

Step 2: Loading environment variables...
✅ Environment variables loaded

Step 3: Checking AWS credentials...
✅ CLOUD_SERVICE: s3
✅ AWS_ACCESS_KEY_ID: AKIA...MPLE
✅ AWS_SECRET_ACCESS_KEY: wJal...EKEY
✅ AWS_S3_BUCKET: ecg-reports-bucket
✅ AWS_S3_REGION: us-east-1

Step 4: Checking boto3 installation...
✅ boto3 is installed

Step 5: Testing AWS S3 connection...
✅ Successfully connected to S3 bucket: ecg-reports-bucket
✅ Region: us-east-1

Step 6: Testing upload permissions...
✅ Upload test successful
✅ Delete test successful

======================================================================
🎉 SUCCESS! Cloud upload is properly configured!
======================================================================
```

### Step 6: Run the Application

```bash
# Run the ECG Monitor
python src/main.py

# OR (if you're in the src directory)
cd src
python main.py
```

---

## ✅ Verify Cloud Sync Works

1. **Login** to the application
2. Go to **"ECG 12 Lead Test"** page
3. Click **"Start"** and record some ECG data (or use demo mode)
4. Click **"Generate Report"**
5. Go back to **Dashboard**
6. Click the **☁️ Cloud Sync** button (top right)
7. Check for success message: **"✅ Synced X files to cloud"**

---

## 🔍 Troubleshooting

### Error: `.env file not found`

**Problem:** The `.env` file doesn't exist in your project root.

**Solution:**
```bash
# Make sure you're in the project root
cd /path/to/modularecg-main

# Copy the template
cp env_template.txt .env

# Edit and add your credentials
nano .env
```

---

### Error: `Cloud Not Configured`

**Problem:** The application can't find or read your `.env` file.

**Solution:**
```bash
# Check if .env exists
ls -la .env

# If missing, create it:
cp env_template.txt .env

# Make sure it's in the project ROOT directory
pwd  # Should show: /path/to/modularecg-main
ls .env  # Should show: .env
```

---

### Error: `Access Denied` or `403 Forbidden`

**Problem:** Your AWS credentials are invalid or don't have permissions.

**Solution:**
1. Double-check your credentials in `.env`
2. Make sure there are **no extra spaces** before/after values
3. Contact Divyansh to verify your IAM user has S3 permissions
4. Required permissions:
   - `s3:PutObject` (upload files)
   - `s3:GetObject` (download files)
   - `s3:ListBucket` (list files)
   - `s3:DeleteObject` (delete files)

---

### Error: `NoSuchBucket`

**Problem:** The bucket name is incorrect or doesn't exist.

**Solution:**
1. Check the bucket name in `.env` (no typos!)
2. Ask Divyansh for the correct bucket name
3. Bucket names are **case-sensitive**

---

### Error: `boto3 not installed`

**Problem:** The boto3 library isn't installed.

**Solution:**
```bash
# Make sure virtual environment is activated
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install boto3
pip install boto3

# Or reinstall all dependencies
pip install -r requirements.txt
```

---

### Cloud Sync Button Shows "Offline"

**Problem:** No internet connection or can't reach AWS.

**Solution:**
1. Check your internet connection
2. Try: `ping aws.amazon.com`
3. Check firewall settings (allow outbound HTTPS on port 443)
4. If on corporate network, check proxy settings

---

## 🔒 Security Best Practices

### ✅ DO:
- ✅ Keep `.env` file **local only** (never commit to Git)
- ✅ Share credentials via **encrypted channels**
- ✅ Use **IAM users** with limited permissions (not root account)
- ✅ Rotate credentials regularly (every 3-6 months)
- ✅ Delete `.env` if you leave the project

### ❌ DON'T:
- ❌ **Never** commit `.env` to GitHub
- ❌ **Never** hardcode credentials in Python files
- ❌ **Never** share credentials in chat/email/Slack
- ❌ **Never** use root AWS account credentials
- ❌ **Never** screenshot your credentials

---

## 📁 File Structure (After Setup)

```
modularecg-main/
├── .env                    # ⚠️ YOUR CREDENTIALS (NOT in Git)
├── env_template.txt        # ✅ Template (safe to commit)
├── test_cloud_connection.py # ✅ Test script
├── requirements.txt        # ✅ Dependencies
├── src/
│   ├── main.py
│   └── utils/
│       └── cloud_uploader.py  # ✅ Handles S3 uploads
└── reports/                # 📄 Local reports (before sync)
```

---

## 🤝 Team Workflow

### For Divyansh (Team Lead):
1. Create IAM users for each team member (PTR, Indresh, Android dev)
2. Give them **limited S3 permissions** (not full admin)
3. Share credentials securely (LastPass, 1Password, or in person)
4. Monitor S3 bucket usage in AWS Console

### For PTR, Indresh, and Team Members:
1. Get credentials from Divyansh
2. Follow this setup guide
3. Run `test_cloud_connection.py` to verify
4. Start developing and testing
5. Cloud sync will work automatically

### For Android Developer:
See `BACKEND_INTEGRATION_PLAN.md` for:
- Direct S3 access using AWS SDK for Android
- Read-only IAM credentials
- Code examples in Kotlin/Java

---

## 📞 Support

**If you encounter issues:**

1. ✅ Run `python3 test_cloud_connection.py` and share the output
2. ✅ Check this troubleshooting guide first
3. ✅ Contact Divyansh if you need new credentials
4. ✅ Check AWS Console for bucket status

**Contact:**
- Team Lead: Divyansh
- Backend: Divyansh, PTR
- Frontend: Indresh
- Android: (Android team member)

---

## 🎯 Summary Checklist

Before you start working, make sure:

- [ ] Repository cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created from `env_template.txt`
- [ ] AWS credentials filled in `.env`
- [ ] Test script passed (`python3 test_cloud_connection.py`)
- [ ] Application runs (`python src/main.py`)
- [ ] Cloud sync button works

**If all checkboxes are ✅, you're ready to go!**

---

**Last Updated:** November 10, 2025  
**Maintainer:** Divyansh  
**Version:** 1.0

