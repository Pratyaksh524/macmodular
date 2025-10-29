# 🚀 AWS S3 Setup for Reports Only

**Purpose:** Configure AWS S3 to receive ONLY ECG reports, metrics, and report files  
**What Won't Be Uploaded:** Session logs, debug files, crash logs, temp files, or any other data

---

## ✅ **What WILL Be Uploaded to AWS S3**

### **Allowed File Types:**
1. **PDF Reports** - Generated ECG reports with patient data
2. **JSON Metrics** - Only files with "report" or "metric" in filename
3. **Report Metadata** - ECG metrics (HR, PR, QRS, QT/QTc, ST, Axis)

### **Allowed Metadata Fields:**
- `patient_name` - Patient name
- `patient_age` - Patient age
- `report_date` - Date of report
- `machine_serial` - Device serial number
- `heart_rate` - Heart rate (BPM)
- `pr_interval` - PR interval (ms)
- `qrs_duration` - QRS duration (ms)
- `qtc_interval` - QT/QTc interval (ms)
- `st_segment` - ST segment (mm)
- `qrs_axis` - QRS axis (degrees)

---

## ❌ **What Will NOT Be Uploaded**

- Session logs (`logs/session_*.log`)
- Crash logs (`logs/crash_logs.json`)
- Error logs (`logs/error_logs.txt`)
- Debug files (any file without "report" or "metric" in name)
- Temp files (`.tmp`, `.cache`, etc.)
- ECG data buffers (raw signal data)
- Configuration files (`ecg_settings.json`)

---

## 🔧 **Setup Instructions**

### **Step 1: Create AWS S3 Bucket**

1. **Go to AWS Console** → S3
2. **Create Bucket:**
   - Bucket name: `ecg-reports-yourname` (must be globally unique)
   - Region: `us-east-1` (or your preferred region)
   - Block all public access: **ON** (recommended)
   - Versioning: Disabled (optional)
3. **Note your bucket name and region**

### **Step 2: Create IAM User for S3 Access**

1. **Go to AWS Console** → IAM
2. **Create User:**
   - User name: `ecg-reports-uploader`
   - Access type: **Programmatic access**
3. **Attach Policy:**
   - Search for: "S3"
   - Select: **AmazonS3FullAccess** (or create custom policy with only `s3:PutObject` permission)
4. **Save Credentials:**
   - Access Key ID
   - Secret Access Key
   - ⚠️ **SAVE THESE - You won't see the secret again!**

### **Step 3: Configure ECG Monitor App**

Create a `.env` file in the project root:

```bash
# AWS S3 Configuration
CLOUD_UPLOAD_ENABLED=true
CLOUD_SERVICE=s3

# AWS Credentials
AWS_S3_BUCKET=ecg-reports-yourname
AWS_S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
```

### **Step 4: Install Required Package**

```bash
pip install boto3
```

Or add to `requirements.txt`:
```
boto3>=1.28.0
```

---

## 📊 **How It Works**

### **Upload Process:**

1. **User generates ECG report** in the app
2. **App checks file name:**
   - Must contain "report" AND be `.pdf` → ✅ **Upload**
   - Must contain "metric" AND be `.json` → ✅ **Upload**
   - Anything else → ❌ **Skip**
3. **App filters metadata:**
   - Only sends allowed fields (patient info, ECG metrics)
   - Removes debug info, logs, temp data
4. **Upload to S3:**
   - Path: `ecg-reports/YYYY/MM/DD/filename.pdf`
   - Includes filtered metadata as S3 object metadata

### **Upload Location in S3:**

```
ecg-reports-yourname/
└── ecg-reports/
    └── 2025/
        └── 10/
            └── 28/
                ├── ECG_Report_20251028_143022.pdf
                └── metrics_20251028_143022.json
```

---

## 🔒 **Security Best Practices**

### **Recommended IAM Policy (Minimal Permissions):**

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:PutObjectAcl"
            ],
            "Resource": "arn:aws:s3:::ecg-reports-yourname/ecg-reports/*"
        }
    ]
}
```

### **Bucket Policy (Optional - Public Read):**

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::ecg-reports-yourname/ecg-reports/*"
        }
    ]
}
```

---

## 🧪 **Testing**

### **Test Upload:**

1. Generate a report in the app
2. Check console output for:
   ```
   ☁️  Uploading report to cloud (s3)...
   ✓ Report uploaded successfully to s3
   ```

3. Verify in AWS S3 Console:
   - Navigate to your bucket
   - Check `ecg-reports/YYYY/MM/DD/` folder
   - Verify PDF file is there
   - Check metadata (click file → Properties → Metadata)

### **Check Upload Log:**

Located at: `reports/upload_log.json`

```json
[
    {
        "local_path": "reports/ECG_Report_20251028_143022.pdf",
        "uploaded_at": "2025-10-28T14:30:22.123456",
        "service": "s3",
        "result": {
            "status": "success",
            "url": "https://ecg-reports-yourname.s3.amazonaws.com/ecg-reports/2025/10/28/ECG_Report_20251028_143022.pdf"
        }
    }
]
```

---

## 📝 **Code Changes Made**

### **File: `src/utils/cloud_uploader.py`**

**Added filtering logic:**
```python
# ONLY upload reports and metrics
is_report = file_ext in allowed_extensions and 'report' in file_basename
is_metric = file_ext == '.json' and 'metric' in file_basename

if not (is_report or is_metric):
    return {"status": "skipped", ...}

# Filter metadata to only allowed fields
allowed_keys = ['patient_name', 'patient_age', ...]
filtered_metadata = {k: v for k, v in metadata.items() if k in allowed_keys}
```

**This ensures:**
- ✅ Only ECG reports are uploaded
- ✅ Only metric data is sent
- ✅ No debug logs uploaded
- ✅ No crash logs uploaded
- ✅ No session logs uploaded

---

## 💰 **AWS S3 Pricing (Approximate)**

For ~100 ECG reports/month (average 1MB each):

- **Storage:** $0.023 per GB/month
  - 100 reports × 1MB = 0.1 GB
  - Cost: ~$0.002/month
- **Upload (PUT requests):** $0.005 per 1,000 requests
  - 100 reports = 100 requests
  - Cost: ~$0.0005/month
- **Download (GET requests):** $0.0004 per 1,000 requests
  - Cost: ~$0.0001/month

**Total Estimated Cost:** **~$0.003/month** (less than $0.05/year)

---

## 🎯 **Summary**

✅ **What Uploads:** Only ECG PDF reports and metrics JSON files  
❌ **What Doesn't Upload:** Logs, debug files, crash reports, temp files  
🔒 **Security:** Private bucket, IAM user with minimal permissions  
💰 **Cost:** Extremely low (~$0.003/month for 100 reports)  
📊 **Organization:** Reports organized by date (YYYY/MM/DD)

---

**Ready to go!** Just create your `.env` file with AWS credentials and the system will automatically upload only reports and metrics to AWS S3.

