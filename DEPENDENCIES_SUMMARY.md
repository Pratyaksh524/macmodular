# 📦 ECG Monitor - Dependencies Summary

## ✅ Complete List of Required Modules

This document provides a comprehensive overview of all Python packages required for the ECG Monitor application.

---

## 🎯 Core Dependencies (15 Packages)

### 1. **GUI Framework**
| Package | Version | Purpose |
|---------|---------|---------|
| `PyQt5` | ≥5.15.0 | Main GUI framework for desktop application |

### 2. **Scientific Computing** (3 packages)
| Package | Version | Purpose |
|---------|---------|---------|
| `numpy` | ≥1.21.0 | Array operations, signal processing |
| `scipy` | ≥1.7.0 | Advanced signal processing (filters, peak detection) |
| `matplotlib` | ≥3.5.0 | Static plotting, report visualizations |

### 3. **Real-Time Data Visualization**
| Package | Version | Purpose |
|---------|---------|---------|
| `pyqtgraph` | ≥0.13.0 | High-performance real-time ECG waveform plotting |

### 4. **Hardware Communication**
| Package | Version | Purpose |
|---------|---------|---------|
| `pyserial` | ≥3.5 | Serial communication with ECG hardware |

### 5. **Data Processing**
| Package | Version | Purpose |
|---------|---------|---------|
| `pandas` | ≥1.3.0 | Data analysis, CSV handling, time series |

### 6. **Media Processing** (2 packages)
| Package | Version | Purpose |
|---------|---------|---------|
| `Pillow` | ≥8.3.0 | Image processing and manipulation |
| `pyaudio` | ≥0.2.11 | Audio playback (heartbeat sounds) |

### 7. **Document Generation**
| Package | Version | Purpose |
|---------|---------|---------|
| `reportlab` | ≥3.6.0 | PDF report generation |

### 8. **Cloud Integration**
| Package | Version | Purpose |
|---------|---------|---------|
| `boto3` | ≥1.26.0 | AWS S3 cloud storage for reports |

### 9. **Configuration Management**
| Package | Version | Purpose |
|---------|---------|---------|
| `python-dotenv` | ≥0.19.0 | Environment variables (.env files) |

### 10. **Network Communication**
| Package | Version | Purpose |
|---------|---------|---------|
| `requests` | ≥2.27.0 | HTTP requests for API calls |

### 11. **Utilities** (3 packages)
| Package | Version | Purpose |
|---------|---------|---------|
| `pyparsing` | ≥3.0.0 | Text parsing utilities |
| `psutil` | ≥5.9.0 | System monitoring, crash logging |
| `numba` | ≥0.56.0 | (Optional) Performance optimization via JIT compilation |

---

## 📚 Standard Library Modules (Included in Python)

These modules are part of Python's standard library and **don't need installation**:

```python
# File I/O and Data
import json          # JSON parsing
import csv           # CSV file handling
import os            # Operating system interface
import sys           # System-specific parameters

# Date and Time
import time          # Time-related functions
from datetime import datetime  # Date/time manipulation

# Concurrency
import threading     # Thread-based parallelism
import queue         # Thread-safe queues

# Networking
import socket        # Low-level networking
import smtplib       # SMTP email protocol
import email         # Email message handling

# Utilities
import traceback     # Exception tracking
import logging       # Logging facility
import math          # Mathematical functions
from typing import * # Type hints
from pathlib import Path  # Object-oriented filesystem paths
from functools import partial  # Higher-order functions
```

---

## 🚀 Installation Instructions

### Step 1: Create Virtual Environment (Recommended)

```bash
# Navigate to project directory
cd /Users/deckmount/Downloads/modularecg-main

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### Step 2: Install All Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

### Step 3: Platform-Specific Setup

#### **macOS Users** (PyAudio requires PortAudio):
```bash
# Install PortAudio via Homebrew
brew install portaudio

# Then install PyAudio
pip install pyaudio
```

#### **Linux Users** (Ubuntu/Debian):
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-pyqt5 portaudio19-dev

# Then install Python packages
pip install -r requirements.txt
```

#### **Windows Users**:
```bash
# Install Visual C++ Build Tools if needed
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Then install packages
pip install -r requirements.txt
```

### Step 4: Configure AWS S3 (Optional - for cloud sync)

Create a `.env` file in the project root:

```bash
# Copy template
cp email_config_template.txt .env

# Edit with your AWS credentials
nano .env
```

Add the following:
```env
CLOUD_SERVICE=s3
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_S3_BUCKET=your_bucket_name
AWS_S3_REGION=us-east-1
```

---

## 🔍 Verify Installation

Run this command to check if all dependencies are installed:

```bash
python3 << 'EOF'
import sys

modules = [
    "PyQt5", "numpy", "scipy", "matplotlib", "pyqtgraph",
    "serial", "pandas", "PIL", "pyaudio", "reportlab",
    "boto3", "dotenv", "requests", "pyparsing", "psutil"
]

missing = []
for module in modules:
    try:
        __import__(module if module != "serial" else "serial")
        print(f"✅ {module}")
    except ImportError:
        print(f"❌ {module} - MISSING")
        missing.append(module)

if missing:
    print(f"\n⚠️  Missing: {', '.join(missing)}")
    sys.exit(1)
else:
    print("\n🎉 All dependencies installed!")
    sys.exit(0)
EOF
```

---

## 📊 Dependency Size Overview

| Category | Packages | Approx. Size |
|----------|----------|-------------|
| Core GUI | 1 | ~50 MB |
| Scientific | 3 | ~150 MB |
| Plotting | 2 | ~30 MB |
| Data/Media | 4 | ~40 MB |
| Cloud/Network | 3 | ~20 MB |
| Utilities | 2 | ~10 MB |
| **TOTAL** | **15** | **~300 MB** |

---

## 🐛 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'PyQt5'`
**Solution:**
```bash
pip install PyQt5
```

### Issue: `ImportError: No module named 'serial'`
**Solution:**
```bash
pip install pyserial
```

### Issue: PyAudio installation fails on macOS
**Solution:**
```bash
brew install portaudio
pip install pyaudio
```

### Issue: `boto3` import error
**Solution:**
```bash
pip install boto3
```

### Issue: Virtual environment not activating
**Solution:**
```bash
# Recreate virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🔄 Updating Dependencies

To update all packages to their latest compatible versions:

```bash
pip install --upgrade -r requirements.txt
```

To update a specific package:

```bash
pip install --upgrade package_name
```

---

## 📝 Version Compatibility

| Python Version | Status | Notes |
|---------------|--------|-------|
| Python 3.8 | ✅ Supported | Minimum recommended |
| Python 3.9 | ✅ Supported | Recommended |
| Python 3.10 | ✅ Supported | Recommended |
| Python 3.11 | ✅ Supported | Latest tested |
| Python 3.12 | ⚠️ Experimental | Some packages may have issues |

---

## 📞 Support

If you encounter any dependency issues:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Verify your Python version: `python --version`
3. Try recreating your virtual environment
4. Check package-specific documentation for platform-specific issues

---

**Last Updated:** November 10, 2025  
**Maintainer:** Divyansh  
**Total Dependencies:** 15 packages + Python standard library

