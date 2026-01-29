# Solution: Localhost Traffic Not Captured

## The Problem

Your attack simulator is working perfectly, but **no alerts appear** because:

**Localhost traffic (`127.0.0.1`) does NOT go through network interfaces!**

When you send traffic to `127.0.0.1`:
- It stays in the kernel's loopback
- Never touches physical network adapters
- Your IDS can't see it (it's capturing on a physical interface)

## Solution Options

### Option 1: Install Npcap Loopback Adapter (Recommended)

**Steps:**
1. Reinstall Npcap with loopback support:
   - Download: https://npcap.com/#download
   - Run installer
   - **CHECK** "Install Npcap in WinPcap API-compatible Mode"
   - **CHECK** "Support loopback traffic"
   
2. Restart your computer

3. In your dashboard, select **"Npcap Loopback Adapter"** interface

4. Run attacks again

### Option 2: Use Your Machine's Real IP

**Find your IP:**
```powershell
ipconfig
# Look for "IPv4 Address" (e.g., 192.168.1.100)
```

**Update attack simulator:**
Edit `scripts/simulate_attacks_gentle.py`:
```python
# Change line 9 from:
TARGET_IP = "127.0.0.1"

# To your actual IP:
TARGET_IP = "192.168.1.100"  # Your IP here
TARGET_URL = f"http://{TARGET_IP}:{TARGET_PORT}"
```

**Update API to listen on all interfaces:**
Edit `config/config.py`:
```python
# Change from:
API_HOST = "0.0.0.0"  # Already correct!
```

Now attacks will go through your actual network interface.

### Option 3: Test with External Traffic (Quick Test)

**Generate real network traffic:**

1. **From another device** on your network (phone, laptop):
   ```
   # Find your PC's IP first (ipconfig)
   # Then from other device:
   curl http://YOUR_PC_IP:8000
   ```

2. **Or use a browser** on the same PC:
   - Visit: `http://YOUR_LOCAL_IP:8000`
   - This forces traffic through the network stack

### Option 4: Use PCAP Files (Testing Alternative)

Instead of live capture, test with pre-recorded traffic:

```bash
# Download sample PCAP with attacks
# Upload via API:
curl -X POST "http://localhost:8000/api/capture/pcap/upload" \
  -F "file=@sample_attack.pcap"
```

## Why This Happens

```
┌─────────────────────────────────────────┐
│  Attack Simulator (127.0.0.1:8000)     │
│         ↓                               │
│    Loopback (kernel)                    │
│         ↓                               │
│    API Server receives request          │
│                                         │
│  ✗ Traffic NEVER touches network card   │
│  ✗ IDS capturing on eth0/WiFi sees     │
│    NOTHING                              │
└─────────────────────────────────────────┘

VS

┌─────────────────────────────────────────┐
│  Attack from 192.168.1.X                │
│         ↓                               │
│    Network Interface (eth0/WiFi)        │
│         ↓                               │
│    IDS CAPTURES packets ✓               │
│         ↓                               │
│    API Server receives request          │
└─────────────────────────────────────────┘
```

## Verification Steps

After implementing a solution:

1. **Check capture is seeing packets:**
   ```bash
   curl http://localhost:8000/api/capture/status
   # Look for: "total_packets" increasing
   ```

2. **Generate traffic and wait 2-3 minutes:**
   - Flows need time to complete
   - Default timeout: 120 seconds

3. **Check for alerts:**
   ```bash
   curl http://localhost:8000/api/alerts
   ```

4. **Check dashboard:**
   - Open: http://localhost:5173
   - Look at Alerts tab

## Quick Test Right Now

**Easiest way to verify IDS is working:**

```powershell
# 1. Stop current capture in dashboard

# 2. Find your IP
ipconfig
# Note your IPv4 address (e.g., 192.168.1.100)

# 3. Edit simulate_attacks_gentle.py
# Change TARGET_IP to your actual IP

# 4. Restart capture with same interface

# 5. Run attacks
python scripts\simulate_attacks_gentle.py ddos

# 6. Wait 2-3 minutes for flows to complete

# 7. Check alerts
curl http://localhost:8000/api/alerts
```

## Expected Output When Working

**API Logs:**
```
Captured packet: TCP 192.168.1.100:54321 -> 192.168.1.100:8000
Flow updated: 192.168.1.100:54321 -> 192.168.1.100:8000
Flow completed: <flow_id>
Extracting features from flow...
Features extracted: 78 features
Making prediction...
Prediction: DDoS (confidence: 0.87)
Broadcasting alert via WebSocket
```

**Dashboard:**
- 🔴 Red alert appears: "DDoS detected"
- Statistics update
- Packet count increases

## Summary

**Your IDS is working correctly!** The issue is:
- ✅ Model loaded
- ✅ Capture running
- ✅ Attack simulator working
- ❌ **Traffic not visible to IDS** (loopback issue)

**Fix:** Use Option 1 (Npcap loopback) or Option 2 (real IP)
