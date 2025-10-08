# 🔌 Backend Integration Plan for ECG Monitor

> **📡 IMPORTANT:** This application now features **offline-first architecture**!  
> See [`OFFLINE_FIRST_ARCHITECTURE.md`](OFFLINE_FIRST_ARCHITECTURE.md) for details on how the app handles online/offline scenarios automatically.

## 📊 Current Frontend Status

### ✅ **Complete Features**

#### 1. **Core ECG Functionality**
- [x] 12-lead ECG real-time visualization
- [x] Live data acquisition from hardware (serial communication)
- [x] Demo mode with synthetic ECG data
- [x] Medical-grade signal filtering (8-stage pipeline)
- [x] Adaptive scaling for different signal amplitudes

#### 2. **Metrics Calculation** (All Real-time)
- [x] **Heart Rate** (BPM) - Pan-Tompkins R-peak detection
- [x] **PR Interval** (ms) - P-wave to QRS onset
- [x] **QRS Duration** (ms) - QRS complex width
- [x] **QRS Axis** (degrees) - Electrical axis calculation
- [x] **ST Segment** (normalized units) - J-point elevation/depression
- [x] **QT Interval** (ms) - Q-onset to T-end
- [x] **QTc Interval** (ms) - Corrected QT (Bazett's formula)
- [x] **HRV** (ms) - Heart rate variability
- [x] **RR Interval** (ms) - Beat-to-beat interval

#### 3. **User Management**
- [x] User authentication (sign in/sign out)
- [x] User registration with full details:
  - Full name, age, gender, address, phone, password
  - Machine serial ID (unique device identifier)
- [x] Password hashing (bcrypt)
- [x] Local user storage (`users.json`)
- [x] Session management

#### 4. **Data Recording & Storage**
- [x] **Session Recording** - JSONL format (`reports/sessions/`)
  - Timestamp
  - Username and user metadata
  - Live metrics (HR, PR, QRS, ST, QTc, etc.)
  - ECG waveform snapshots (5-second windows, all 12 leads)
  - Arrhythmia detection events
- [x] **PDF Report Generation**
  - Patient demographics
  - ECG waveform graphs (all 12 leads with pink medical grid)
  - Calculated metrics
  - Arrhythmia analysis
  - AI-generated conclusions
- [x] **Upload Logging** (`reports/upload_log.json`)
  - Tracks all successful cloud uploads
  - Includes metadata and cloud URLs

#### 5. **Cloud Upload System** ☁️
- [x] Automatic upload after report generation
- [x] Support for 6 cloud services:
  - AWS S3
  - Azure Blob Storage
  - Google Cloud Storage
  - Custom API endpoint
  - FTP/SFTP
  - Dropbox
- [x] Configurable via `.env` file
- [x] Upload logging and error handling

#### 6. **UI Components**
- [x] Dashboard with live metrics
- [x] 12-lead grid view
- [x] Expanded lead view (detailed analysis)
- [x] Recent reports panel
- [x] Settings panel (wave speed, gain, etc.)
- [x] Crash logger dialog
- [x] Chatbot integration (Google Gemini)

#### 7. **Error Handling & Logging**
- [x] Crash detection and logging
- [x] Email reporting for crashes
- [x] Serial communication error handling
- [x] Automatic error recovery

---

## 🎯 **Backend Requirements & Data Flow**

### **Primary Data Types to Send to Backend:**

#### **1. Real-time Metrics Stream**
**Frequency:** Every 1-2 seconds during active recording

**Data Structure:**
```json
{
  "type": "metrics_update",
  "timestamp": "2025-01-08T12:34:56.789Z",
  "device_serial": "ECG-12345",
  "user_id": "unique_user_id",
  "session_id": "session_20250108_123456",
  "metrics": {
    "heart_rate": 75,
    "pr_interval": 160,
    "qrs_duration": 85,
    "qrs_axis": 45,
    "st_segment": 0,
    "qt_interval": 380,
    "qtc_interval": 400,
    "hrv": 45,
    "rr_interval": 800,
    "sampling_rate": 80
  },
  "status": {
    "is_recording": true,
    "signal_quality": "good",
    "demo_mode": false
  }
}
```

#### **2. ECG Waveform Data Stream**
**Frequency:** Batch upload every 5-10 seconds or on-demand

**Data Structure:**
```json
{
  "type": "ecg_waveform",
  "timestamp": "2025-01-08T12:34:56.789Z",
  "device_serial": "ECG-12345",
  "user_id": "unique_user_id",
  "session_id": "session_20250108_123456",
  "sampling_rate": 80,
  "duration_seconds": 5,
  "leads": {
    "I": [0.123, 0.145, 0.167, ...],    // 400 samples (5 sec * 80 Hz)
    "II": [0.234, 0.256, 0.278, ...],
    "III": [0.111, 0.133, 0.155, ...],
    "aVR": [-0.123, -0.145, ...],
    "aVL": [0.056, 0.078, ...],
    "aVF": [0.167, 0.189, ...],
    "V1": [0.089, 0.111, ...],
    "V2": [0.123, 0.145, ...],
    "V3": [0.178, 0.200, ...],
    "V4": [0.234, 0.256, ...],
    "V5": [0.189, 0.211, ...],
    "V6": [0.145, 0.167, ...]
  }
}
```

#### **3. Session Start Event**
**Frequency:** Once at session start

**Data Structure:**
```json
{
  "type": "session_start",
  "timestamp": "2025-01-08T12:30:00.000Z",
  "device_serial": "ECG-12345",
  "user": {
    "user_id": "unique_user_id",
    "full_name": "John Doe",
    "age": 45,
    "gender": "Male",
    "phone": "+1234567890",
    "address": "123 Main St, City, State",
    "registration_date": "2025-01-01"
  },
  "session_id": "session_20250108_123456",
  "device_info": {
    "os": "darwin 25.0.0",
    "app_version": "1.0.0",
    "sampling_rate": 80
  }
}
```

#### **4. Session End Event**
**Frequency:** Once at session end or app close

**Data Structure:**
```json
{
  "type": "session_end",
  "timestamp": "2025-01-08T13:00:00.000Z",
  "session_id": "session_20250108_123456",
  "device_serial": "ECG-12345",
  "user_id": "unique_user_id",
  "summary": {
    "duration_seconds": 1800,
    "total_heartbeats": 2250,
    "average_heart_rate": 75,
    "arrhythmias_detected": ["PVC", "PAC"],
    "signal_quality": "good"
  }
}
```

#### **5. Generated Report Upload**
**Frequency:** When user generates a PDF report

**Data Structure:**
```json
{
  "type": "report_generated",
  "timestamp": "2025-01-08T13:00:00.000Z",
  "device_serial": "ECG-12345",
  "user_id": "unique_user_id",
  "session_id": "session_20250108_123456",
  "report": {
    "filename": "ECG_Report_20250108_130000.pdf",
    "file_url": "https://storage.example.com/reports/ECG_Report_20250108_130000.pdf",
    "file_size_bytes": 1234567,
    "patient_name": "John Doe",
    "patient_age": 45,
    "metrics": {
      "heart_rate": 75,
      "pr_interval": 160,
      "qrs_duration": 85,
      "qtc_interval": 400,
      "st_segment": 0
    },
    "conclusion": "Normal sinus rhythm. No significant abnormalities detected."
  }
}
```

#### **6. Arrhythmia Detection Event**
**Frequency:** Real-time when detected

**Data Structure:**
```json
{
  "type": "arrhythmia_detected",
  "timestamp": "2025-01-08T12:35:23.456Z",
  "device_serial": "ECG-12345",
  "user_id": "unique_user_id",
  "session_id": "session_20250108_123456",
  "arrhythmia": {
    "type": "PVC",
    "severity": "mild",
    "description": "Premature Ventricular Contraction",
    "heart_rate_at_event": 78,
    "lead": "II",
    "waveform_snippet": [0.123, 0.456, 0.789, ...]  // 2-3 seconds around event
  }
}
```

#### **7. Error/Crash Report**
**Frequency:** When errors occur

**Data Structure:**
```json
{
  "type": "error_report",
  "timestamp": "2025-01-08T12:40:00.000Z",
  "device_serial": "ECG-12345",
  "user_id": "unique_user_id",
  "session_id": "session_20250108_123456",
  "error": {
    "error_type": "serial_communication_error",
    "error_message": "Failed to read from port /dev/ttyUSB0",
    "stack_trace": "...",
    "system_info": {
      "os": "darwin 25.0.0",
      "python_version": "3.13",
      "memory_usage_mb": 450
    }
  }
}
```

---

## 🔧 **Backend API Endpoints Needed**

### **1. Authentication & User Management**

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "full_name": "John Doe",
  "age": 45,
  "gender": "Male",
  "phone": "+1234567890",
  "address": "123 Main St",
  "password": "hashed_password",
  "device_serial": "ECG-12345"
}

Response: 
{
  "user_id": "unique_user_id",
  "token": "jwt_token_here"
}
```

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "identifier": "John Doe",  // Can be full_name or device_serial
  "password": "hashed_password"
}

Response:
{
  "user_id": "unique_user_id",
  "token": "jwt_token_here",
  "user_profile": { ... }
}
```

### **2. Session Management**

```http
POST /api/v1/sessions/start
Authorization: Bearer jwt_token
Content-Type: application/json

{
  "device_serial": "ECG-12345",
  "device_info": { ... }
}

Response:
{
  "session_id": "session_20250108_123456"
}
```

```http
POST /api/v1/sessions/{session_id}/end
Authorization: Bearer jwt_token
Content-Type: application/json

{
  "summary": { ... }
}

Response:
{
  "status": "success"
}
```

### **3. Real-time Data Upload**

```http
POST /api/v1/sessions/{session_id}/metrics
Authorization: Bearer jwt_token
Content-Type: application/json

{
  "timestamp": "2025-01-08T12:34:56.789Z",
  "metrics": { ... }
}

Response:
{
  "status": "success",
  "metrics_id": "metric_12345"
}
```

```http
POST /api/v1/sessions/{session_id}/waveform
Authorization: Bearer jwt_token
Content-Type: application/json

{
  "timestamp": "2025-01-08T12:34:56.789Z",
  "sampling_rate": 80,
  "leads": { ... }
}

Response:
{
  "status": "success",
  "waveform_id": "waveform_67890"
}
```

### **4. Report Upload**

```http
POST /api/v1/reports/upload
Authorization: Bearer jwt_token
Content-Type: multipart/form-data

file: <PDF file>
metadata: <JSON metadata>

Response:
{
  "status": "success",
  "report_id": "report_12345",
  "url": "https://storage.example.com/reports/ECG_Report_20250108_130000.pdf"
}
```

### **5. Data Retrieval**

```http
GET /api/v1/users/{user_id}/sessions
Authorization: Bearer jwt_token

Response:
{
  "sessions": [
    {
      "session_id": "session_20250108_123456",
      "start_time": "2025-01-08T12:30:00Z",
      "end_time": "2025-01-08T13:00:00Z",
      "duration_seconds": 1800,
      "average_heart_rate": 75
    },
    ...
  ]
}
```

```http
GET /api/v1/sessions/{session_id}/data
Authorization: Bearer jwt_token

Response:
{
  "session_id": "session_20250108_123456",
  "metrics_timeline": [ ... ],
  "waveform_segments": [ ... ],
  "reports": [ ... ]
}
```

---

## 💻 **Frontend Implementation Plan**

### **Step 1: Create Backend Communication Module**

Create `src/utils/backend_api.py`:

```python
import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class BackendAPI:
    """Handle all backend communication"""
    
    def __init__(self):
        self.base_url = os.getenv('BACKEND_API_URL', 'http://localhost:3000/api/v1')
        self.api_key = os.getenv('BACKEND_API_KEY')
        self.token = None
        self.session_id = None
        
    def set_token(self, token: str):
        """Set JWT token for authenticated requests"""
        self.token = token
        
    def _headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        elif self.api_key:
            headers['X-API-Key'] = self.api_key
        return headers
    
    def register_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new user"""
        response = requests.post(
            f'{self.base_url}/auth/register',
            json=user_data,
            headers=self._headers(),
            timeout=10
        )
        return response.json()
    
    def login(self, identifier: str, password: str) -> Dict[str, Any]:
        """Login user"""
        response = requests.post(
            f'{self.base_url}/auth/login',
            json={'identifier': identifier, 'password': password},
            headers=self._headers(),
            timeout=10
        )
        data = response.json()
        if 'token' in data:
            self.set_token(data['token'])
        return data
    
    def start_session(self, device_serial: str, device_info: Dict) -> str:
        """Start a new recording session"""
        response = requests.post(
            f'{self.base_url}/sessions/start',
            json={'device_serial': device_serial, 'device_info': device_info},
            headers=self._headers(),
            timeout=10
        )
        data = response.json()
        self.session_id = data.get('session_id')
        return self.session_id
    
    def upload_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Upload real-time metrics"""
        if not self.session_id:
            return {"status": "error", "message": "No active session"}
        
        payload = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'metrics': metrics
        }
        
        response = requests.post(
            f'{self.base_url}/sessions/{self.session_id}/metrics',
            json=payload,
            headers=self._headers(),
            timeout=5
        )
        return response.json()
    
    def upload_waveform(self, leads_data: Dict[str, list], sampling_rate: int) -> Dict[str, Any]:
        """Upload ECG waveform data"""
        if not self.session_id:
            return {"status": "error", "message": "No active session"}
        
        payload = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'sampling_rate': sampling_rate,
            'leads': leads_data
        }
        
        response = requests.post(
            f'{self.base_url}/sessions/{self.session_id}/waveform',
            json=payload,
            headers=self._headers(),
            timeout=10
        )
        return response.json()
    
    def upload_report(self, pdf_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Upload generated PDF report"""
        with open(pdf_path, 'rb') as f:
            files = {'file': f}
            data = {'metadata': json.dumps(metadata)}
            
            response = requests.post(
                f'{self.base_url}/reports/upload',
                files=files,
                data=data,
                headers={'Authorization': f'Bearer {self.token}'} if self.token else {},
                timeout=30
            )
            return response.json()
    
    def end_session(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """End current session"""
        if not self.session_id:
            return {"status": "error", "message": "No active session"}
        
        response = requests.post(
            f'{self.base_url}/sessions/{self.session_id}/end',
            json={'summary': summary},
            headers=self._headers(),
            timeout=10
        )
        self.session_id = None
        return response.json()

# Global instance
_backend_api = None

def get_backend_api() -> BackendAPI:
    """Get or create global backend API instance"""
    global _backend_api
    if _backend_api is None:
        _backend_api = BackendAPI()
    return _backend_api
```

### **Step 2: Update `.env` Configuration**

Add to `.env` file:
```env
# Backend API Configuration
BACKEND_UPLOAD_ENABLED=true
BACKEND_API_URL=http://localhost:3000/api/v1
BACKEND_API_KEY=your_api_key_here

# Or use production URL
# BACKEND_API_URL=https://api.your-domain.com/v1
```

### **Step 3: Integration Points**

**In `src/ecg/twelve_lead_test.py`:**
- Call `backend_api.upload_metrics()` every 2 seconds in `update_plots()`
- Call `backend_api.upload_waveform()` every 10 seconds with batch of lead data

**In `src/ecg/ecg_report_generator.py`:**
- After PDF generation, call `backend_api.upload_report()`

**In `src/main.py`:**
- On login: call `backend_api.login()`
- On session start: call `backend_api.start_session()`
- On app close: call `backend_api.end_session()`

---

## 📈 **Backend Architecture Recommendations**

### **Tech Stack Options**

#### **Option 1: Node.js + Express + MongoDB (Recommended)**
```javascript
// Pros: Fast, scalable, good for real-time data
// Stack: Node.js, Express, MongoDB, Socket.io (for WebSocket)
```

#### **Option 2: Python + FastAPI + PostgreSQL**
```python
# Pros: Same language as frontend, easy integration
# Stack: FastAPI, PostgreSQL/TimescaleDB, Redis
```

#### **Option 3: Django + PostgreSQL**
```python
# Pros: Full-featured, admin panel, ORM
# Stack: Django, PostgreSQL, Celery, Redis
```

### **Database Schema**

```sql
-- Users table
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    full_name VARCHAR(255),
    age INT,
    gender VARCHAR(50),
    phone VARCHAR(50),
    address TEXT,
    device_serial VARCHAR(100),
    password_hash VARCHAR(255),
    created_at TIMESTAMP,
    last_login TIMESTAMP
);

-- Sessions table
CREATE TABLE sessions (
    session_id VARCHAR(100) PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    device_serial VARCHAR(100),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_seconds INT,
    average_heart_rate FLOAT,
    status VARCHAR(50)
);

-- Metrics table (time-series data)
CREATE TABLE metrics (
    metric_id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) REFERENCES sessions(session_id),
    timestamp TIMESTAMP,
    heart_rate INT,
    pr_interval INT,
    qrs_duration INT,
    qtc_interval INT,
    st_segment FLOAT,
    -- ... other metrics
);

-- Waveform data (consider TimescaleDB for time-series)
CREATE TABLE waveforms (
    waveform_id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) REFERENCES sessions(session_id),
    timestamp TIMESTAMP,
    sampling_rate INT,
    lead_i FLOAT[],
    lead_ii FLOAT[],
    -- ... other leads
);

-- Reports table
CREATE TABLE reports (
    report_id VARCHAR(100) PRIMARY KEY,
    session_id VARCHAR(100) REFERENCES sessions(session_id),
    user_id UUID REFERENCES users(user_id),
    file_url TEXT,
    created_at TIMESTAMP,
    conclusion TEXT
);
```

---

## ✅ **Next Steps**

1. **Choose backend technology** (Node.js/Python/Django)
2. **Set up backend infrastructure** (server, database, storage)
3. **Implement API endpoints** from the list above
4. **Create `backend_api.py`** module in frontend
5. **Integrate API calls** at key points in the app
6. **Test end-to-end** data flow
7. **Deploy backend** to cloud (AWS, Azure, GCP, or your own server)
8. **Update frontend** `.env` with production URLs

Your frontend is **100% ready** to integrate with a backend! All the data structures, session recording, and cloud upload infrastructure are already in place. You just need to:
1. Build the backend APIs
2. Connect the frontend using the `backend_api.py` module

Let me know if you'd like help with any specific part! 🚀

