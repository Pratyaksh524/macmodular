# Hardware Protocol Comparison: Current vs New

## Overview
This document compares the **current ASCII-based protocol** with the **new binary protocol** for ECG data transmission.

---

## 1. DATA FORMAT

### Current Implementation (ASCII Text)
```
Format: Plain text numbers separated by spaces
Example: "2100 2050 2150 2200 2050 2100 2150 2200"
Size: Variable (typically 30-50 bytes as text)
Encoding: UTF-8 text
```

**What we receive:**
```python
# From serial port:
"2100 2050 2150 2200 2050 2100 2150 2200\r\n"

# After parsing:
[2100, 2050, 2150, 2200, 2050, 2100, 2150, 2200]
```

### New Implementation (Binary)
```
Format: 22-byte binary packet with fixed structure
Size: Always exactly 22 bytes
Encoding: Binary (raw bytes)
```

**What we will receive:**
```python
# From serial port (hex representation):
E8 00 11 20 15 7F 3F 7F 3F 7F 3F 7F 3F 7F 3F 7F 3F 7F 3F 7F 3F 8E

# Byte breakdown:
[0xE8]                    # Start marker
[0x00]                    # Counter (0-63)
[0x11]                    # Length = 17 bytes
[0x20]                    # OpCode
[0x15]                    # Checksum
[0x7F, 0x3F]             # Lead I  (LSB, MSB)
[0x7F, 0x3F]             # Lead II (LSB, MSB)
[0x7F, 0x3F]             # V1     (LSB, MSB)
[0x7F, 0x3F]             # V2     (LSB, MSB)
[0x7F, 0x3F]             # V3     (LSB, MSB)
[0x7F, 0x3F]             # V4     (LSB, MSB)
[0x7F, 0x3F]             # V5     (LSB, MSB)
[0x7F, 0x3F]             # V6     (LSB, MSB)
[0x8E]                    # End marker
```

---

## 2. READING DATA FROM SERIAL PORT

### Current Code (twelve_lead_test.py, line 219-262)
```python
def read_value(self):
    # Read until newline character
    line_raw = self.ser.readline()
    
    # Decode as UTF-8 text
    line_data = line_raw.decode('utf-8', errors='replace').strip()
    
    # Parse space-separated numbers
    values = [int(x) for x in cleaned_line.split()]
    
    # Return list of 8 integers
    return values  # e.g., [2100, 2050, 2150, 2200, 2050, 2100, 2150, 2200]
```

### New Code (Required)
```python
def read_value(self):
    # Read exactly 22 bytes (fixed packet size)
    packet = self.ser.read(22)
    
    # Validate packet structure
    if len(packet) != 22:
        return None
    
    # Check start and end markers
    if packet[0] != 0xE8 or packet[21] != 0x8E:
        print("❌ Invalid packet markers")
        return None
    
    # Extract metadata
    counter = packet[1]
    length = packet[2]
    opcode = packet[3]
    checksum_received = packet[4]
    
    # Validate checksum
    checksum_calculated = self._calculate_checksum(packet[5:21])
    if checksum_received != checksum_calculated:
        print("❌ Checksum mismatch")
        return None
    
    # Extract 8 ECG lead values
    values = []
    connection_status = []
    
    for i in range(8):
        lsb_idx = 5 + (i * 2)
        msb_idx = 6 + (i * 2)
        
        lsb = packet[lsb_idx]
        msb = packet[msb_idx]
        
        # Extract 12-bit signal value
        signal_value = ((msb & 0x1F) << 7) | (lsb & 0x7F)
        values.append(signal_value)
        
        # Extract connection status (bit 5 of MSB)
        is_connected = bool(msb & 0x20)
        connection_status.append(is_connected)
    
    # Return both signal values and connection status
    return {
        'counter': counter,
        'values': values,
        'connections': connection_status
    }
```

---

## 3. SIGNAL VALUE ENCODING

### Current (Simple Integer)
```python
# Direct integer value (0-4095 range typically)
signal = 2100
```

### New (12-bit in Two Bytes)
```python
# Example: Signal value = 2100 (0x834 in hex)
# Binary: 0000 1000 0011 0100

LSB (Byte 1):
  Bit 7: 0 (always zero)
  Bits 6-0: 0110100 (lower 7 bits of signal) = 0x34

MSB (Byte 2):
  Bit 6: Additional status (Lead II only)
  Bit 5: Connection status (1=connected, 0=disconnected)
  Bits 4-0: 01000 (upper 5 bits of signal) = 0x08

# To decode:
signal = ((MSB & 0x1F) << 7) | (LSB & 0x7F)
signal = (0x08 << 7) | 0x34
signal = 1024 + 52 = 1076

# To encode (if we need to send data):
LSB = signal & 0x7F
MSB = (signal >> 7) & 0x1F
```

---

## 4. NEW FEATURES WE NEED TO ADD

### A. Connection Status Detection
**Current:** No way to know if leads are connected
**New:** Each lead has a connection status bit

```python
# Current: Can't detect disconnected leads
values = [2100, 2050, 2150, 2200, 2050, 2100, 2150, 2200]

# New: Know which leads are connected
connections = [True, True, False, True, True, True, False, True]
                #      #             V1 disconnected      V5 disconnected
```

**UI Changes Needed:**
- Show red indicator for disconnected leads
- Display "Lead Off" message
- Don't calculate metrics from disconnected leads

### B. Packet Validation
**Current:** No validation (trust whatever comes)
**New:** Multiple validation checks

```python
# Checks needed:
1. Start marker == 0xE8
2. End marker == 0x8E
3. Length field == 0x11 (17 bytes)
4. Checksum validation
5. Counter sequence (detect missing packets)
```

### C. Error Detection
**Current:** Only detect serial port errors
**New:** Detect multiple error types

```python
# New errors we can detect:
- Corrupted packets (bad checksum)
- Missing packets (counter jump)
- Sync loss (bad markers)
- Lead disconnection
```

---

## 5. CONNECTION STATUS MAPPING

### Lead Connection Bits
```
Lead I:  MSB1[bit 5] = LA (Left Arm) status
Lead II: MSB2[bit 5] = RA (Right Arm) status
         MSB2[bit 6] = LL (Left Leg) status
V1:      MSB3[bit 5]
V2:      MSB4[bit 5]
V3:      MSB5[bit 5]
V4:      MSB6[bit 5]
V5:      MSB7[bit 5]
V6:      MSB8[bit 5]
```

### Code to Extract
```python
def get_connection_status(msb_byte, lead_type):
    """Extract connection status from MSB byte"""
    if lead_type == 'lead_ii_ll':
        # Special case: Lead II LL uses bit 6
        return bool(msb_byte & 0x40)
    else:
        # All other leads use bit 5
        return bool(msb_byte & 0x20)
```

---

## 6. CHECKSUM CALCULATION

**Current:** No checksum
**New:** Need checksum algorithm from hardware team

```python
# Placeholder (waiting for hardware team's formula)
def _calculate_checksum(self, data_bytes):
    """
    Calculate checksum for data integrity
    
    Common methods:
    1. Simple sum: sum(data_bytes) & 0xFF
    2. XOR: reduce(lambda a,b: a^b, data_bytes)
    3. CRC-8: (more complex)
    
    TODO: Get exact formula from hardware team
    """
    # Example (simple sum modulo 256):
    return sum(data_bytes) & 0xFF
```

---

## 7. COMPLETE CODE COMPARISON

### Current read_value() - 44 lines
```python
def read_value(self):
    if not self.running:
        return None
    try:
        line_raw = self.ser.readline()
        line_data = line_raw.decode('utf-8', errors='replace').strip()

        if line_data:
            self.data_count += 1
            print(f"📡 [Packet #{self.data_count}] Raw data: '{line_data}'")
            
            if line_data.isdigit():
                ecg_value = int(line_data[-3:])
                return ecg_value
            else:
                try:
                    import re
                    cleaned_line = re.sub(r'[^\d\s\-]', ' ', line_data)
                    values = [int(x) for x in cleaned_line.split() 
                             if x.strip() and x.replace('-', '').isdigit()]
                    
                    if len(values) >= 8:
                        print(f"💓 8-Channel ECG Data: {values}")
                        return values
                    # ... more parsing logic
                except Exception as e:
                    print(f"❌ Error parsing: {e}")
                    return None
    except Exception as e:
        self._handle_serial_error(e)
    return None
```

### New read_value() - Will be ~80 lines
```python
def read_value(self):
    if not self.running:
        return None
    
    try:
        # 1. READ FIXED 22 BYTES
        packet = self.ser.read(22)
        
        if len(packet) != 22:
            print(f"⚠️ Incomplete packet: {len(packet)} bytes")
            return None
        
        # 2. VALIDATE FRAME MARKERS
        if packet[0] != 0xE8:
            print(f"❌ Invalid start marker: 0x{packet[0]:02X}")
            return None
        
        if packet[21] != 0x8E:
            print(f"❌ Invalid end marker: 0x{packet[21]:02X}")
            return None
        
        # 3. EXTRACT METADATA
        counter = packet[1]
        length = packet[2]
        opcode = packet[3]
        checksum_received = packet[4]
        
        # 4. VALIDATE LENGTH
        if length != 0x11:
            print(f"❌ Invalid length: {length}")
            return None
        
        # 5. VALIDATE CHECKSUM
        checksum_calculated = self._calculate_checksum(packet[5:21])
        if checksum_received != checksum_calculated:
            print(f"❌ Checksum mismatch: got 0x{checksum_received:02X}, "
                  f"expected 0x{checksum_calculated:02X}")
            return None
        
        # 6. DETECT MISSING PACKETS
        if hasattr(self, '_last_counter'):
            expected = (self._last_counter + 1) % 64
            if counter != expected and self.data_count > 0:
                dropped = (counter - expected) % 64
                print(f"⚠️ {dropped} packet(s) dropped "
                      f"(counter jump: {self._last_counter} → {counter})")
        self._last_counter = counter
        
        # 7. DECODE 8 ECG LEADS
        values = []
        connections = {}
        
        for i in range(8):
            lsb_idx = 5 + (i * 2)
            msb_idx = 6 + (i * 2)
            
            lsb = packet[lsb_idx]
            msb = packet[msb_idx]
            
            # Extract 12-bit signal
            signal = ((msb & 0x1F) << 7) | (lsb & 0x7F)
            values.append(signal)
            
            # Extract connection status
            lead_names = ['Lead_I', 'Lead_II', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
            is_connected = bool(msb & 0x20)
            connections[lead_names[i]] = is_connected
            
            # Special: Lead II also has LL status in bit 6
            if i == 1:  # Lead II
                connections['LL'] = bool(msb & 0x40)
        
        self.data_count += 1
        
        # 8. RETURN STRUCTURED DATA
        return {
            'counter': counter,
            'values': values,
            'connections': connections,
            'timestamp': time.time()
        }
        
    except Exception as e:
        self._handle_serial_error(e)
        return None

def _calculate_checksum(self, data_bytes):
    """Calculate checksum (TODO: get formula from hardware team)"""
    return sum(data_bytes) & 0xFF
```

---

## 8. CHANGES TO update_plots()

### Current (line ~6000+)
```python
def update_plots(self):
    value = self.serial_reader.read_value()
    
    if value is None:
        return
    
    # If it's a list of 8 values, use them directly
    if isinstance(value, list) and len(value) == 8:
        raw_8_channel = value
    else:
        # Single value - replicate to 8 channels
        raw_8_channel = [value] * 8
    
    # Convert 8 channels to 12 leads
    leads_12 = self.calculate_12_leads_from_8_channels(raw_8_channel)
    
    # Plot the data
    for i, lead_value in enumerate(leads_12):
        self.data[i] = np.roll(self.data[i], -1)
        self.data[i][-1] = lead_value
        self.data_lines[i].setData(self.data[i])
```

### New (Required Changes)
```python
def update_plots(self):
    packet_data = self.serial_reader.read_value()
    
    if packet_data is None:
        return
    
    # NEW: Extract values and connection status
    if isinstance(packet_data, dict):
        raw_8_channel = packet_data['values']
        connections = packet_data['connections']
        counter = packet_data['counter']
    else:
        # Fallback for old format during transition
        raw_8_channel = packet_data if isinstance(packet_data, list) else [packet_data] * 8
        connections = {f'Lead_{i}': True for i in range(8)}
    
    # Convert 8 channels to 12 leads
    leads_12 = self.calculate_12_leads_from_8_channels(raw_8_channel)
    
    # NEW: Update connection status UI
    self._update_connection_indicators(connections)
    
    # Plot the data
    for i, lead_value in enumerate(leads_12):
        lead_name = self.leads[i]
        
        # NEW: Show "LEAD OFF" if disconnected
        if not self._is_lead_connected(lead_name, connections):
            self._show_lead_disconnected(i)
            continue
        
        # Normal plotting
        self.data[i] = np.roll(self.data[i], -1)
        self.data[i][-1] = lead_value
        self.data_lines[i].setData(self.data[i])

# NEW HELPER FUNCTIONS NEEDED
def _update_connection_indicators(self, connections):
    """Update UI to show which leads are connected"""
    for lead_name, is_connected in connections.items():
        indicator = self.connection_indicators.get(lead_name)
        if indicator:
            if is_connected:
                indicator.setStyleSheet("background: green; border-radius: 5px;")
            else:
                indicator.setStyleSheet("background: red; border-radius: 5px;")

def _is_lead_connected(self, lead_name, connections):
    """Check if a specific lead is connected"""
    # Map 12-lead names to 8-channel connection status
    lead_mapping = {
        'I': 'Lead_I',
        'II': 'Lead_II',
        'III': ['Lead_I', 'Lead_II'],  # Derived from I and II
        'aVR': ['Lead_I', 'Lead_II'],
        'aVL': ['Lead_I', 'Lead_II'],
        'aVF': ['Lead_II', 'LL'],
        'V1': 'V1',
        'V2': 'V2',
        'V3': 'V3',
        'V4': 'V4',
        'V5': 'V5',
        'V6': 'V6'
    }
    
    required = lead_mapping.get(lead_name, [])
    if isinstance(required, str):
        return connections.get(required, True)
    else:
        return all(connections.get(r, True) for r in required)

def _show_lead_disconnected(self, lead_index):
    """Display 'LEAD OFF' message on plot"""
    # Clear the plot
    self.data[lead_index].fill(0)
    self.data_lines[lead_index].setData(self.data[lead_index])
    
    # Show warning text overlay
    # (Implementation depends on your plotting library)
```

---

## 9. SUMMARY OF CHANGES

| Component | Current | New | Complexity |
|-----------|---------|-----|------------|
| **Data Format** | ASCII text | Binary (22 bytes) | Medium |
| **Reading** | `readline()` | `read(22)` | Low |
| **Parsing** | Split & convert to int | Bitwise operations | Medium |
| **Validation** | None | Start/end markers + checksum | Medium |
| **Connection Status** | Not available | Per-lead monitoring | High |
| **Error Detection** | Basic | Advanced (packets, sync) | Medium |
| **UI Updates** | None needed | Connection indicators | High |
| **Code Changes** | ~100 lines | ~300 lines total | Medium |

### Files to Modify
1. `src/ecg/twelve_lead_test.py` - Main changes (SerialECGReader class, update_plots)
2. `src/ecg/twelve_lead_test.py` - Add connection indicator UI elements
3. Testing file - Create test harness for binary packets

### Estimated Timeline
- **Code implementation**: 8-12 hours
- **UI for connection status**: 3-4 hours  
- **Testing with real hardware**: 4-6 hours
- **Documentation**: 2 hours
- **Total**: 17-24 hours (~2-3 days)

---

## 10. QUESTIONS FOR HARDWARE TEAM

Before starting implementation, we need:

1. ✅ **Checksum Formula**: Exact algorithm (sum? XOR? CRC-8?)
2. ✅ **Signal Range**: What do values 0-4095 represent in mV?
3. ✅ **Sampling Rate**: How many packets per second?
4. ✅ **Transition Plan**: Support both protocols or hard cutover?
5. ✅ **Test Data**: Sample binary packets for testing without hardware?

---

## CONCLUSION

**Main Difference**: 
- **Before**: Simple text parsing, no validation, no status info
- **After**: Binary protocol with validation, checksums, and connection monitoring

**Difficulty**: Medium complexity, very feasible
**Risk**: Low (hardware protocols are well-defined)
**Recommendation**: **Proceed** once hardware team provides checksum formula

