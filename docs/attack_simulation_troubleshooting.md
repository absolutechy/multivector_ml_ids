# Attack Simulation Troubleshooting Guide

## Problem: API Server Crashes During DDoS Simulation

### Symptoms
- `ValueError: too many file descriptors in select()`
- Server becomes unresponsive
- Connection refused errors

### Root Cause
Windows has a limit on the number of open file descriptors (sockets) that can be monitored by `select()`. The aggressive DDoS simulation opens too many sockets simultaneously.

### Solutions

#### Option 1: Use Gentle Simulator (Recommended)
```bash
python scripts\simulate_attacks_gentle.py all
```

This version:
- Controls request rate (15-20 req/s instead of unlimited)
- Properly closes all sockets
- Won't crash your server
- Still generates enough traffic for IDS detection

#### Option 2: Reduce Thread Count
Edit `scripts\simulate_attacks.py`:
```python
# Change from:
simulate_ddos(30, threads=15)

# To:
simulate_ddos(30, threads=3)
```

#### Option 3: Use HTTP Requests Instead of Raw Sockets
The gentle simulator uses `requests` library which handles connection pooling better than raw sockets.

---

## Why Alerts Don't Appear

### Issue 1: Live Capture vs API Traffic
**Problem:** Your IDS is capturing network interface traffic, but the attack simulator targets `127.0.0.1` (localhost loopback).

**Solution:** Loopback traffic may not appear on all network interfaces. You have two options:

**A. Capture Loopback Traffic:**
- Install "Npcap Loopback Adapter" during Npcap installation
- Select the loopback interface in your dashboard
- Restart capture

**B. Target Real Network Interface:**
```python
# In simulate_attacks.py, change:
TARGET_IP = "127.0.0.1"

# To your actual IP:
TARGET_IP = "192.168.1.X"  # Your machine's IP
```

### Issue 2: Model Not Detecting Attacks
**Problem:** Model was trained on CICIDS2017 dataset which has specific traffic patterns.

**Reasons:**
1. **Feature Mismatch:** Simulated attacks may not match training data features
2. **Flow Aggregation:** IDS aggregates packets into flows before prediction
3. **Timing:** Need sustained traffic for flow completion

**Solutions:**

**A. Check Flow Completion:**
Live capture aggregates packets into flows. A flow completes when:
- Connection closes (FIN/RST)
- Timeout (default: 120 seconds)
- Flow becomes idle

**B. Generate More Sustained Traffic:**
```bash
# Run for longer duration
python scripts\simulate_attacks_gentle.py ddos
# Let it run for 2-3 minutes
```

**C. Check API Logs:**
Look for:
```
Prediction worker started
Flow completed: <flow_id>
Prediction: <attack_type>
```

### Issue 3: WebSocket Not Broadcasting
**Problem:** Predictions made but not sent to frontend.

**Check:**
1. WebSocket connected? (Check browser console)
2. Backend logs show broadcasts?
3. Frontend receiving messages?

**Debug:**
```bash
# Check alerts via API
curl http://localhost:8000/api/alerts

# Check statistics
curl http://localhost:8000/api/statistics
```

---

## Best Practices for Testing

### 1. Start Simple
```bash
# Test with gentle simulator first
python scripts\simulate_attacks_gentle.py benign
```

### 2. Monitor Both Sides
- **Terminal 1:** API server logs
- **Terminal 2:** Attack simulator
- **Browser:** Dashboard (http://localhost:5173)

### 3. Check Capture Status
Before running attacks:
1. Verify model loaded: ✓ Loaded
2. Verify capture running: 🟢 Capturing
3. Check packet count increasing

### 4. Use PCAP Files (Alternative)
Instead of live simulation:
```bash
# Upload pre-recorded attack PCAP
curl -X POST "http://localhost:8000/api/capture/pcap/upload" \
  -F "file=@attack.pcap"
```

---

## Expected Behavior

### Successful Attack Detection Flow

1. **Attack Simulator Runs:**
   ```
   [23:52:42] [WARNING] Starting DDoS ATTACK simulation...
   [23:52:47] [WARNING] DDoS in progress... 5s | Requests sent: 150
   ```

2. **Live Capture Sees Packets:**
   ```
   Captured packet: TCP 127.0.0.1:54321 -> 127.0.0.1:8000
   Flow updated: 127.0.0.1:54321 -> 127.0.0.1:8000
   ```

3. **Flow Completes & Prediction:**
   ```
   Flow completed: <flow_id>
   Extracting features...
   Features extracted: 78 features
   Making prediction...
   Prediction: DDoS (confidence: 0.87)
   ```

4. **Alert Broadcast:**
   ```
   Broadcasting alert via WebSocket
   Alert saved to memory
   ```

5. **Frontend Shows Alert:**
   - Red alert appears in Alerts tab
   - Statistics updated
   - Attack distribution chart updated

---

## Quick Fixes

### If Server Keeps Crashing
```bash
# Use gentle simulator with low rate
python scripts\simulate_attacks_gentle.py ddos
```

### If No Alerts Appear
```bash
# 1. Check if model is loaded
curl http://localhost:8000/api/model/info

# 2. Check capture status
curl http://localhost:8000/api/capture/status

# 3. Check existing alerts
curl http://localhost:8000/api/alerts

# 4. Try direct API attack (bypasses capture)
curl "http://localhost:8000/?id=' OR '1'='1"
```

### If WebSocket Disconnects
- Refresh browser
- Check CORS settings
- Verify WebSocket URL: `ws://localhost:8000/ws`

---

## Alternative: Test with Real Traffic

Instead of simulated attacks, capture real network traffic:

1. **Browse websites** (benign)
2. **Download large files** (high bandwidth)
3. **Run network scans** (nmap - only on your own network!)
4. **Use penetration testing tools** (in lab environment)

---

## Summary

**For Reliable Testing:**
1. Use `simulate_attacks_gentle.py` instead of `simulate_attacks.py`
2. Ensure loopback adapter is installed and selected
3. Let attacks run for 2-3 minutes for flow completion
4. Monitor API logs for prediction output
5. Check `/api/alerts` endpoint directly if dashboard doesn't update

**The attack simulator IS working** - it successfully overwhelmed your server (that's what DDoS does!). Now we need to:
- Make it gentler (done ✓)
- Ensure traffic is captured on the right interface
- Wait for flows to complete before expecting predictions
