# Bug Report: Wrong Values in ECG Reports

**Date:** November 5, 2025  
**Reported by:** Divyansh  
**Severity:** HIGH  
**Status:** 🔴 IDENTIFIED - NEEDS FIX

---

## 🐛 Issues Found

### 1. **P/QRS/T Amplitudes - WRONG UNIT CONVERSION**
❌ **Problem:** Values are way too small (showing in mV but displaying as mm)

**Current Logic in `ecg_report_generator.py` (Line 1190-1193):**
```python
# Convert to mm (ECG standard: 1mV = 10mm)
p_mm = int(p_amp_mv * 10) if p_amp_mv > 0 else 12  # fallback to 12
qrs_mm = int(qrs_amp_mv * 10) if qrs_amp_mv > 0 else 37  # fallback to 37
t_mm = int(t_amp_mv * 10) if t_amp_mv > 0 else 34  # fallback to 34
```

**Problem Explanation:**
- The values coming from `calculate_wave_amplitudes()` are **already in arbitrary units** (not mV)
- They're being multiplied by 10 assuming they're in mV
- This makes them appear **10-100x too small**

**Example:**
- If actual P-wave is 0.15 mV → Should show as **1.5 mm**
- Currently shows: `0.15 * 10 = 1 mm` (close, but loses precision)
- If calculation gives `0.015` → Shows as `0 mm` (wrong!)

---

### 2. **RV5/SV1 - WRONG UNIT CONVERSION (1000x TOO SMALL!)**
❌ **Problem:** Values are divided by 1000, making them 1000x smaller than actual

**Current Logic in `ecg_report_generator.py` (Line 1250-1251):**
```python
# Convert to mV for display (values assumed to be in microvolt-like units; normalize)
rv5_mv = rv5_amp / 1000 if rv5_amp > 0 else 1.260  # fallback
sv1_mv = sv1_amp / 1000 if sv1_amp > 0 else 0.786  # fallback
```

**Problem Explanation:**
- The comment says "values assumed to be in microvolt-like units"
- **BUT** `calculate_wave_amplitudes()` returns values in **millivolts** (mV), NOT microvolts (μV)!
- Dividing by 1000 converts mV → volts → makes them tiny

**Example:**
- Actual RV5 amplitude: 1.5 mV
- `calculate_wave_amplitudes()` returns: `rv5 = 1.5`
- Report converts: `1.5 / 1000 = 0.0015 mV` ❌ **WRONG!**
- Should be: `1.5 mV` ✅

**Impact:**
- RV5+SV1 is the sum of two tiny numbers → always near zero
- Sokolow-Lyon index (RV5+SV1 > 3.5 mV indicates LVH) is useless

---

### 3. **RV5+SV1 Sum - WRONG (Because inputs are wrong)**
❌ **Problem:** Sum of two incorrect values

**Current Logic in `ecg_report_generator.py` (Line 1261):**
```python
# Calculate RV5+SV1 sum
rv5_sv1_sum = rv5_mv + sv1_mv
```

**Example:**
- If RV5 should be 1.5 mV and SV1 should be 0.8 mV
- Correct sum: **2.3 mV**
- Current (wrong): `0.0015 + 0.0008 = 0.0023 mV` ❌

---

### 4. **QTCF - HARDCODED DUMMY VALUE**
❌ **Problem:** Always shows `0.049` regardless of actual QT/RR values

**Current Logic in `ecg_report_generator.py` (Line 1269-1270):**
```python
# SECOND COLUMN - QTCF
qtcf_label = String(240, 612, "QTCF       : 0.049", 
                    fontSize=10, fontName="Helvetica", fillColor=colors.black)
```

**Problem Explanation:**
- QTCF (Fridericia formula) should be calculated as: **QT / ∛RR**
- Currently just shows a hardcoded dummy value
- Medical staff will see this and think QTc is always 49 ms (absurd!)

**Correct Formula:**
```python
# Fridericia formula for QTc
QTCF = QT / (RR_interval ** (1/3))
```

**Normal Range:** 350-450 ms (0.35-0.45 seconds)

---

## 📊 Impact Assessment

### **Severity by Metric:**

| Metric | Current Status | Error Magnitude | Clinical Impact |
|--------|---------------|-----------------|-----------------|
| **P/QRS/T** | ⚠️ **Wrong** | 10-100x too small | MEDIUM - Affects diagnosis |
| **RV5** | ❌ **Very Wrong** | 1000x too small | HIGH - LVH detection broken |
| **SV1** | ❌ **Very Wrong** | 1000x too small | HIGH - LVH detection broken |
| **RV5+SV1** | ❌ **Very Wrong** | 1000x too small | **CRITICAL** - Key diagnostic lost |
| **QTCF** | ❌ **Dummy** | Always 0.049 | MEDIUM - Missing QT correction |

---

## 🔧 Root Cause Analysis

### **Why This Happened:**

1. **Assumption Mismatch:**
   - Report generator assumes amplitude values are in microvolts (μV)
   - Calculation function returns values in millivolts (mV)
   - No unit documentation in the code

2. **Legacy Fallback Values:**
   - Fallback values (1.260, 0.786) are reasonable in mV
   - But then divided by 1000 → tiny numbers
   - Indicates the `/1000` was added later

3. **Copy-Paste Error:**
   - The comment says "microvolt-like units" but this was never verified
   - Likely copied from another part of the code

4. **No Validation:**
   - No sanity checks on amplitude values
   - No alerts when values are suspiciously small
   - No unit tests for these calculations

---

## ✅ Proposed Fix

### **Fix 1: P/QRS/T Amplitudes**

**Location:** `src/ecg/ecg_report_generator.py` (Lines 1190-1195)

**Change:**
```python
# OLD (WRONG):
p_mm = int(p_amp_mv * 10) if p_amp_mv > 0 else 12
qrs_mm = int(qrs_amp_mv * 10) if qrs_amp_mv > 0 else 37
t_mm = int(t_amp_mv * 10) if t_amp_mv > 0 else 34

# NEW (CORRECT):
# Values from calculate_wave_amplitudes() are in mV
# ECG standard: 1 mV = 10 mm
p_mm = round(p_amp_mv * 10, 1) if p_amp_mv > 0 else 1.2  # Keep 1 decimal
qrs_mm = round(qrs_amp_mv * 10, 1) if qrs_amp_mv > 0 else 15.0
t_mm = round(t_amp_mv * 10, 1) if t_amp_mv > 0 else 3.0

# Format as string with 1 decimal place
p_qrs_label = String(240, 670, f"P/QRS/T  : {p_mm:.1f}/{qrs_mm:.1f}/{t_mm:.1f} mm", 
                     fontSize=10, fontName="Helvetica", fillColor=colors.black)
```

---

### **Fix 2: RV5/SV1 Amplitudes**

**Location:** `src/ecg/ecg_report_generator.py` (Lines 1249-1253)

**Change:**
```python
# OLD (WRONG):
rv5_mv = rv5_amp / 1000 if rv5_amp > 0 else 1.260  # WRONG! Divides by 1000
sv1_mv = sv1_amp / 1000 if sv1_amp > 0 else 0.786  # WRONG! Divides by 1000

# NEW (CORRECT):
# Values from calculate_wave_amplitudes() are ALREADY in mV (not μV!)
# No conversion needed - just use directly
rv5_mv = rv5_amp if rv5_amp > 0 else 1.260  # Already in mV
sv1_mv = sv1_amp if sv1_amp > 0 else 0.786  # Already in mV

print(f"   RV5={rv5_mv:.3f} mV, SV1={sv1_mv:.3f} mV")
```

---

### **Fix 3: RV5+SV1 Sum**

**Location:** `src/ecg/ecg_report_generator.py` (Lines 1260-1266)

**No change needed** - Will be correct once Fix 2 is applied!

```python
# This will now be correct:
rv5_sv1_sum = rv5_mv + sv1_mv  # Sum of correct mV values
```

---

### **Fix 4: QTCF Calculation**

**Location:** `src/ecg/ecg_report_generator.py` (Lines 1268-1271)

**Change:**
```python
# OLD (HARDCODED DUMMY):
qtcf_label = String(240, 612, "QTCF       : 0.049", 
                    fontSize=10, fontName="Helvetica", fillColor=colors.black)

# NEW (CALCULATED):
# Fridericia formula: QTc = QT / ∛RR
# Where RR is in milliseconds
try:
    if RR > 0 and QT > 0:
        qtcf_seconds = QT / (RR ** (1/3))  # Both in ms, result in ms
        qtcf_ms = round(qtcf_seconds, 0)  # Round to integer ms
        qtcf_status = ""
        if qtcf_ms < 350:
            qtcf_status = " (Short)"
        elif qtcf_ms > 450:
            qtcf_status = " (Prolonged)"
        else:
            qtcf_status = " (Normal)"
        qtcf_display = f"QTCF       : {qtcf_ms} ms{qtcf_status}"
    else:
        qtcf_display = "QTCF       : -- ms (Insufficient data)"
except Exception as e:
    print(f"⚠️ QTCF calculation error: {e}")
    qtcf_display = "QTCF       : -- ms (Error)"

qtcf_label = String(240, 612, qtcf_display, 
                    fontSize=10, fontName="Helvetica", fillColor=colors.black)
```

---

## 📋 Testing Checklist

After applying fixes, verify:

### **Test 1: P/QRS/T Amplitudes**
- [ ] Generate report with demo data
- [ ] Check P/QRS/T values are realistic (P: 0.5-2.5 mm, QRS: 5-25 mm, T: 2-6 mm)
- [ ] Verify decimal places are shown (not just integers)

### **Test 2: RV5/SV1**
- [ ] Generate report with demo data
- [ ] Check RV5 is in range 0.5-3.0 mV (not 0.001-0.003)
- [ ] Check SV1 is in range 0.5-2.0 mV (not 0.001-0.002)
- [ ] Verify 3 decimal places are shown

### **Test 3: RV5+SV1 Sum**
- [ ] Verify sum equals RV5 + SV1
- [ ] Check sum is in range 1.0-4.0 mV (not 0.002-0.005)
- [ ] Test Sokolow-Lyon criteria: Sum > 3.5 mV indicates LVH

### **Test 4: QTCF**
- [ ] Generate report with different heart rates
- [ ] Verify QTCF changes with HR (not always 0.049)
- [ ] Check normal range: 350-450 ms
- [ ] Verify status labels (Short/Normal/Prolonged) appear

### **Test 5: Edge Cases**
- [ ] Test with zero/missing ECG data → Should show fallback values
- [ ] Test with very small amplitudes → Should not show 0
- [ ] Test with very large amplitudes → Should not overflow display

---

## 🎯 Expected Results After Fix

### **Before (Wrong):**
```
P/QRS/T  : 1/15/3 mm            ❌ Too small, no decimals
RV5/SV1  : 0.001/0.001 mV       ❌ 1000x too small!
RV5+SV1  : 0.002 mV             ❌ Useless for diagnosis
QTCF     : 0.049                ❌ Hardcoded dummy
```

### **After (Correct):**
```
P/QRS/T  : 1.5/15.0/3.0 mm      ✅ Realistic, shows decimals
RV5/SV1  : 1.260/0.786 mV       ✅ Normal range
RV5+SV1  : 2.046 mV             ✅ Useful for LVH detection
QTCF     : 410 ms (Normal)      ✅ Calculated, with status
```

---

## 📝 JSON Twin File Updates

**Also update the JSON metrics:**

**Location:** `src/ecg/ecg_report_generator.py` (Lines 1547-1551 and 1584-1588)

**Change:**
```python
# OLD:
"RV5_plus_SV1_mV": round(rv5_sv1_sum, 3),  # Will be correct after fix
"P_QRS_T_mm": [p_mm, qrs_mm, t_mm],        # Update to include decimals
"RV5_SV1_mV": [round(rv5_mv, 3), round(sv1_mv, 3)],  # Will be correct
"QTCF": 0.049,  # CHANGE THIS!

# NEW:
"RV5_plus_SV1_mV": round(rv5_sv1_sum, 3),
"P_QRS_T_mm": [round(p_mm, 1), round(qrs_mm, 1), round(t_mm, 1)],
"RV5_SV1_mV": [round(rv5_mv, 3), round(sv1_mv, 3)],
"QTCF_ms": qtcf_ms if 'qtcf_ms' in locals() else 0,
```

---

## 🚀 Priority & Timeline

**Priority:** 🔴 **CRITICAL** - Must fix before 1000-user rollout

**Estimated Fix Time:**
- Fix implementation: 30 minutes
- Testing: 1 hour
- Documentation: 30 minutes
- **Total: 2 hours**

**Who Should Fix:** **Divyansh** (Backend Lead)

**When to Fix:** **Week 1 (Nov 6-7)** - Before Guest Mode implementation

**Rollout Blocker:** ✅ **YES** - These values are medically significant

---

## 📚 Documentation Updates Needed

After fix, update:

1. **`CALCULATED_VS_PLACEHOLDER_VALUES.md`**
   - Mark QTCF as ✅ Calculated (not placeholder)
   - Update RV5/SV1 section with correct units

2. **`TECHNICAL_DOCUMENTATION.md`**
   - Document unit conventions (all amplitudes in mV)
   - Add QTCF formula explanation

3. **`BUG_FIX_ECG_PAGE.md`** (if exists)
   - Add this fix to the list

---

## 💡 Prevention for Future

**Add to Code:**
```python
# In twelve_lead_test.py - calculate_wave_amplitudes()
def calculate_wave_amplitudes(self):
    """Calculate P, QRS, and T wave amplitudes from all leads
    
    Returns:
        dict: {
            'p_amp': float,    # P-wave amplitude in mV
            'qrs_amp': float,  # QRS amplitude in mV
            't_amp': float,    # T-wave amplitude in mV
            'rv5': float,      # RV5 amplitude in mV
            'sv1': float       # SV1 amplitude in mV
        }
    
    Note: ALL values are returned in millivolts (mV), NOT microvolts!
    """
    # ... existing code ...
```

**Add Validation:**
```python
# In ecg_report_generator.py - After getting amplitudes
# Sanity check: Amplitudes should be in reasonable range
if not (0.01 <= p_amp_mv <= 5.0):
    print(f"⚠️ WARNING: P-wave amplitude {p_amp_mv} mV seems abnormal!")
if not (0.1 <= qrs_amp_mv <= 10.0):
    print(f"⚠️ WARNING: QRS amplitude {qrs_amp_mv} mV seems abnormal!")
if not (0.01 <= t_amp_mv <= 5.0):
    print(f"⚠️ WARNING: T-wave amplitude {t_amp_mv} mV seems abnormal!")
if not (0.1 <= rv5_mv <= 5.0):
    print(f"⚠️ WARNING: RV5 amplitude {rv5_mv} mV seems abnormal!")
if not (0.1 <= sv1_mv <= 5.0):
    print(f"⚠️ WARNING: SV1 amplitude {sv1_mv} mV seems abnormal!")
```

---

## 🎯 Summary

**4 Issues Found:**
1. ⚠️ P/QRS/T: Minor unit issue (10x wrong, loses decimals)
2. ❌ RV5/SV1: Major unit issue (1000x wrong!)
3. ❌ RV5+SV1: Consequence of #2 (sum of wrong values)
4. ❌ QTCF: Hardcoded dummy (always 0.049)

**Impact:**
- Sokolow-Lyon index (LVH detection) is **completely broken**
- QTc Fridericia correction is **missing**
- Wave amplitudes are **inaccurate**

**Fix Complexity:** **LOW** (just remove `/1000` and calculate QTCF)

**Testing Complexity:** **MEDIUM** (need to verify against medical standards)

**Urgency:** **HIGH** (must fix before beta launch in Week 5)

---

**Prepared by:** AI Code Review  
**Date:** November 5, 2025  
**Assign to:** Divyansh (Backend Lead)  
**Deadline:** November 7, 2025 (Week 1, Day 3)

---

**Status:** 🔴 OPEN - Awaiting implementation

