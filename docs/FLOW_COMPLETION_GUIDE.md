# Quick Test Script - Forces Flow Completion

This script helps test your IDS by generating traffic that creates and completes flows quickly.

## The Problem

Your IDS is capturing packets (7,088 packets, 408 active flows) but:
- **0 Completed Flows** = No predictions = No alerts
- Flows complete after 120 seconds of inactivity (too long for testing!)

## Solution Applied

**Changed `config/config.py`:**
```python
FLOW_TIMEOUT = 30  # Reduced from 120 seconds
```

Now flows complete after just 30 seconds of inactivity.

## How to Test

### Step 1: Restart API Server
```bash
# Stop current API (Ctrl+C)
# Restart to load new config
python src\api\main.py
```

### Step 2: Restart Capture
- Stop capture in dashboard
- Start capture again (selects Npcap Loopback)

### Step 3: Run Attack
```bash
python scripts\simulate_attacks_gentle.py ddos
```

### Step 4: Wait 30-45 Seconds
- Watch "Completed Flows" counter
- Should start increasing after ~30 seconds
- Alerts will appear when flows complete

### Step 5: Check Results
```bash
# Check alerts via API
curl http://localhost:8000/api/alerts

# Or check dashboard
# Open: http://localhost:5173
```

## Expected Timeline

```
Time    Event
----    -----
0:00    Start attack simulation
0:00    Packets captured (counter increases)
0:00    Active flows created (408 flows)
0:30    Attack ends
1:00    Flows start timing out (30s after last packet)
1:00    Completed flows: 1, 2, 3... (counter increases)
1:00    Predictions made
1:00    🔴 ALERTS APPEAR! 🔴
```

## Why This Happens

**Flow Lifecycle:**
1. **Packet arrives** → Flow created (Active Flows +1)
2. **More packets** → Flow updated (same flow)
3. **No packets for 30s** → Flow times out
4. **Flow completes** → Features extracted → Prediction made → Alert!

**Your situation:**
- ✅ Step 1-2: Working (7,088 packets, 408 flows)
- ❌ Step 3-4: Waiting for timeout (was 120s, now 30s)

## Alternative: Force Immediate Completion

If you want INSTANT results, modify the attack simulator to close connections properly:

**Edit `scripts/simulate_attacks_gentle.py`:**

```python
def gentle_ddos(duration=30, rate=10):
    """Gentle DDoS with proper connection closing."""
    log(f"Starting gentle DDoS (rate: {rate} req/s, duration: {duration}s)", "WARNING")
    
    end_time = time.time() + duration
    count = 0
    delay = 1.0 / rate
    
    while time.time() < end_time:
        try:
            # Use session with connection close
            session = requests.Session()
            session.headers.update({'Connection': 'close'})
            session.get(TARGET_URL, timeout=2)
            session.close()  # Force close
            count += 1
            if count % 50 == 0:
                log(f"Sent {count} requests", "INFO")
        except Exception as e:
            log(f"Request failed: {e}", "WARNING")
        
        time.sleep(delay)
    
    log(f"Gentle DDoS complete. Total: {count} requests", "SUCCESS")
```

This forces TCP FIN packets, completing flows immediately.

## Verification

**Check if it's working:**

```bash
# Watch the capture status
curl http://localhost:8000/api/capture/status

# Look for:
# "completed_flows": 0  → Should increase after 30s
```

**When working, you'll see:**
```json
{
  "is_running": true,
  "capture": {
    "total_packets": 7088,
    "active_flows": 408,
    "completed_flows": 156  ← This should increase!
  }
}
```

## Summary

**Current Status:**
- ✅ Packets captured: 7,088
- ✅ Active flows: 408
- ❌ Completed flows: 0 (waiting for timeout)

**Fix Applied:**
- Changed timeout: 120s → 30s

**Next Steps:**
1. Restart API server
2. Restart capture
3. Run attack
4. Wait 30-45 seconds
5. See alerts! 🎉
