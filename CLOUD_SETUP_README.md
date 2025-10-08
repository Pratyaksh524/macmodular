# ☁️ Cloud Upload Setup Guide for ECG Monitor

This guide will help you configure automatic cloud upload for ECG reports from your desktop application.

## 📋 Overview

When enabled, the ECG Monitor will automatically upload all generated reports (PDFs and session data) to your chosen cloud storage service. This ensures:
- ✅ Automatic backup of all patient reports
- ✅ Access reports from anywhere
- ✅ Centralized storage for multiple ECG devices
- ✅ HIPAA-compliant storage options available

---

## 🚀 Quick Start (3 Steps)

### Step 1: Choose Your Cloud Service

Pick ONE option that works best for you:

| Service | Best For | Cost | Setup Difficulty |
|---------|----------|------|------------------|
| **Custom API** | Your own server | Your server cost | ⭐ Easy |
| **FTP/SFTP** | Hospital servers | Free (your server) | ⭐ Easy |
| **Dropbox** | Small clinics | Free (2GB) | ⭐⭐ Moderate |
| **AWS S3** | Large scale | Pay-as-you-go | ⭐⭐⭐ Advanced |
| **Azure Blob** | Windows enterprise | Pay-as-you-go | ⭐⭐⭐ Advanced |
| **Google Cloud** | Research facilities | Pay-as-you-go | ⭐⭐⭐ Advanced |

### Step 2: Configure Settings

1. **Copy the template file:**
   ```bash
   # Copy cloud_config_template.txt to .env
   cp cloud_config_template.txt .env
   ```
   
   OR append to existing `.env` file:
   ```bash
   cat cloud_config_template.txt >> .env
   ```

2. **Edit `.env` file** with your settings (see detailed instructions below)

3. **Install required packages** (if needed):
   ```bash
   # For AWS S3
   pip install boto3
   
   # For Azure
   pip install azure-storage-blob
   
   # For Google Cloud
   pip install google-cloud-storage
   
   # For SFTP
   pip install paramiko
   
   # For Dropbox
   pip install dropbox
   ```

### Step 3: Test Upload

1. Start the ECG Monitor application
2. Generate a test report
3. Check terminal output for upload confirmation:
   ```
   ✓ ECG Report generated: reports/ECG_Report_20250108_123456.pdf
   ☁️  Uploading report to cloud (api)...
   ✓ Report uploaded successfully to api
     URL: https://your-domain.com/reports/ECG_Report_20250108_123456.pdf
   ```

---

## 📖 Detailed Setup Instructions

### Option 1: Custom API Endpoint (RECOMMENDED)

**Perfect for:** Most users, custom backends, maximum control

**Requirements:**
- A web server (Apache, Nginx, Node.js, etc.)
- PHP, Python, Node.js, or any language that can receive file uploads

**Setup:**

1. **Create upload endpoint** on your server:

   **PHP Example** (`upload.php`):
   ```php
   <?php
   $api_key = "YOUR_SECRET_API_KEY_HERE";
   
   // Verify API key
   $headers = getallheaders();
   if (!isset($headers['Authorization']) || 
       $headers['Authorization'] !== "Bearer $api_key") {
       http_response_code(401);
       die(json_encode(["error" => "Unauthorized"]));
   }
   
   // Handle file upload
   if (isset($_FILES['file'])) {
       $upload_dir = "/var/www/html/ecg-reports/";
       if (!is_dir($upload_dir)) mkdir($upload_dir, 0755, true);
       
       $filename = date('Y-m-d_His_') . basename($_FILES['file']['name']);
       $target_file = $upload_dir . $filename;
       
       if (move_uploaded_file($_FILES['file']['tmp_name'], $target_file)) {
           echo json_encode([
               "status" => "success",
               "url" => "https://your-domain.com/ecg-reports/" . $filename,
               "message" => "File uploaded successfully"
           ]);
       } else {
           http_response_code(500);
           echo json_encode(["error" => "Upload failed"]);
       }
   } else {
       http_response_code(400);
       echo json_encode(["error" => "No file provided"]);
   }
   ?>
   ```

2. **Configure `.env`:**
   ```env
   CLOUD_UPLOAD_ENABLED=true
   CLOUD_SERVICE=api
   CLOUD_API_ENDPOINT=https://your-domain.com/upload.php
   CLOUD_API_KEY=YOUR_SECRET_API_KEY_HERE
   ```

3. **Test:** Generate a report and check your server's `ecg-reports` folder

---

### Option 2: FTP/SFTP Server

**Perfect for:** Hospital internal servers, existing FTP servers

**Setup:**

1. **Ensure FTP/SFTP server is running** on your server

2. **Configure `.env`:**
   ```env
   CLOUD_UPLOAD_ENABLED=true
   CLOUD_SERVICE=sftp
   FTP_HOST=ftp.your-hospital.com
   FTP_PORT=22
   FTP_USERNAME=ecg_upload_user
   FTP_PASSWORD=your_secure_password
   FTP_REMOTE_PATH=/ecg-reports
   ```

3. **Install SFTP support** (if using SFTP):
   ```bash
   pip install paramiko
   ```

---

### Option 3: Dropbox

**Perfect for:** Small clinics, easy setup, no server needed

**Setup:**

1. **Create Dropbox App:**
   - Go to https://www.dropbox.com/developers/apps
   - Click "Create app"
   - Choose "Scoped access" → "Full Dropbox" → Name your app
   - In "Permissions" tab, enable `files.content.write`
   - In "Settings" tab, generate an access token

2. **Configure `.env`:**
   ```env
   CLOUD_UPLOAD_ENABLED=true
   CLOUD_SERVICE=dropbox
   DROPBOX_ACCESS_TOKEN=sl.xxxxxxxxxxxxxxxxxxxxxxxxx
   ```

3. **Install Dropbox SDK:**
   ```bash
   pip install dropbox
   ```

---

### Option 4: AWS S3

**Perfect for:** Large deployments, healthcare facilities, HIPAA compliance

**Setup:**

1. **Create S3 Bucket:**
   - Log in to AWS Console
   - Go to S3 → Create bucket
   - Choose a unique name (e.g., `your-clinic-ecg-reports`)
   - Enable versioning and encryption

2. **Create IAM User:**
   - Go to IAM → Users → Add user
   - Enable "Programmatic access"
   - Attach policy: `AmazonS3FullAccess` (or custom policy)
   - Save Access Key ID and Secret Access Key

3. **Configure `.env`:**
   ```env
   CLOUD_UPLOAD_ENABLED=true
   CLOUD_SERVICE=s3
   AWS_S3_BUCKET=your-clinic-ecg-reports
   AWS_S3_REGION=us-east-1
   AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
   AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

4. **Install AWS SDK:**
   ```bash
   pip install boto3
   ```

---

### Option 5: Azure Blob Storage

**Perfect for:** Windows environments, Microsoft enterprise healthcare

**Setup:**

1. **Create Storage Account:**
   - Log in to Azure Portal
   - Create new Storage Account
   - Create a container named `ecg-reports`

2. **Get Connection String:**
   - Go to Storage Account → Access keys
   - Copy connection string

3. **Configure `.env`:**
   ```env
   CLOUD_UPLOAD_ENABLED=true
   CLOUD_SERVICE=azure
   AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
   AZURE_CONTAINER_NAME=ecg-reports
   ```

4. **Install Azure SDK:**
   ```bash
   pip install azure-storage-blob
   ```

---

### Option 6: Google Cloud Storage

**Perfect for:** Google Workspace integration, research facilities

**Setup:**

1. **Create GCS Bucket:**
   - Go to Google Cloud Console
   - Create new bucket
   - Choose storage class and location

2. **Create Service Account:**
   - Go to IAM & Admin → Service Accounts
   - Create service account with Storage Admin role
   - Create and download JSON key

3. **Configure `.env`:**
   ```env
   CLOUD_UPLOAD_ENABLED=true
   CLOUD_SERVICE=gcs
   GCS_BUCKET_NAME=your-clinic-ecg-reports
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   ```

4. **Install Google Cloud SDK:**
   ```bash
   pip install google-cloud-storage
   ```

---

## 📊 Upload Log

All successful uploads are logged in `reports/upload_log.json`:

```json
[
  {
    "local_path": "reports/ECG_Report_20250108_123456.pdf",
    "uploaded_at": "2025-01-08T12:34:56",
    "service": "api",
    "result": {
      "status": "success",
      "url": "https://your-domain.com/reports/ECG_Report_20250108_123456.pdf"
    },
    "metadata": {
      "patient_name": "John Doe",
      "patient_age": "45",
      "report_date": "08/01/2025",
      "heart_rate": "75"
    }
  }
]
```

---

## 🔒 Security Best Practices

1. **Never commit `.env` file to Git** - It contains sensitive credentials
2. **Use HTTPS/SFTP** - Always use encrypted connections
3. **Rotate API keys** - Change keys periodically
4. **Enable encryption** - Use server-side encryption for cloud storage
5. **Set proper permissions** - Restrict access to authorized users only
6. **HIPAA Compliance** - For healthcare use, ensure your cloud provider is HIPAA-compliant (AWS, Azure, Google Cloud offer HIPAA plans)

---

## 🐛 Troubleshooting

### Upload Not Working?

1. **Check terminal output** for error messages
2. **Verify `.env` configuration** - Ensure no typos
3. **Test network connectivity** - Can you reach your cloud service?
4. **Check permissions** - Does your API key/user have upload permissions?
5. **Review upload log** - Check `reports/upload_log.json` for details

### Common Errors:

| Error | Solution |
|-------|----------|
| "Cloud upload not configured" | Set `CLOUD_UPLOAD_ENABLED=true` in `.env` |
| "boto3 not installed" | Run `pip install boto3` (or package for your service) |
| "401 Unauthorized" | Check API key, access credentials |
| "404 Not Found" | Verify endpoint URL, bucket name |
| "Connection refused" | Check FTP host, port, firewall |

---

## 📞 Support

For issues or questions:
1. Check the detailed comments in `cloud_config_template.txt`
2. Review error messages in terminal
3. Check `reports/upload_log.json` for upload history

---

## 🎯 Next Steps

After successful setup:
- ✅ Reports automatically upload after generation
- ✅ Check upload log for confirmation
- ✅ Access reports from your cloud storage
- ✅ Configure multiple ECG devices to use same cloud storage

Happy monitoring! 🏥💙

