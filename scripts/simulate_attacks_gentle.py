"""
Gentle Attack Simulator - For Testing Without Crashing
Simulates attacks at a controlled rate that won't overwhelm the system.
"""

import requests
import time
import sys
from datetime import datetime

TARGET_URL = "http://127.0.0.1:8000"

def log(message, level="INFO"):
    """Print timestamped log message."""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] [{level}] {message}")

def gentle_ddos(duration=30, rate=10):
    """
    Gentle DDoS - sends requests at controlled rate.
    
    Args:
        duration: How long to run (seconds)
        rate: Requests per second
    """
    log(f"Starting gentle DDoS (rate: {rate} req/s, duration: {duration}s)", "WARNING")
    
    end_time = time.time() + duration
    count = 0
    delay = 1.0 / rate  # Delay between requests
    
    while time.time() < end_time:
        try:
            requests.get(TARGET_URL, timeout=2)
            count += 1
            if count % 50 == 0:
                log(f"Sent {count} requests", "INFO")
        except Exception as e:
            log(f"Request failed: {e}", "WARNING")
        
        time.sleep(delay)
    
    log(f"Gentle DDoS complete. Total: {count} requests", "SUCCESS")

def web_attacks():
    """Send web attack payloads slowly."""
    log("Starting web attacks...", "WARNING")
    
    payloads = [
        ("SQLi", "/?id=' OR '1'='1"),
        ("SQLi", "/?id=1; DROP TABLE users--"),
        ("SQLi", "/?id=' UNION SELECT NULL--"),
        ("XSS", "/?q=<script>alert('XSS')</script>"),
        ("XSS", "/?q=<img src=x onerror=alert(1)>"),
    ]
    
    for attack_type, payload in payloads:
        try:
            url = f"{TARGET_URL}{payload}"
            response = requests.get(url, timeout=3)
            log(f"{attack_type}: {payload[:40]}... | Status: {response.status_code}", "WARNING")
        except Exception as e:
            log(f"Request failed: {e}", "ERROR")
        
        time.sleep(2)  # 2 second delay between attacks
    
    log("Web attacks complete", "SUCCESS")

def benign_traffic(duration=20):
    """Generate normal traffic."""
    log(f"Starting benign traffic ({duration}s)", "INFO")
    
    end_time = time.time() + duration
    count = 0
    
    while time.time() < end_time:
        try:
            requests.get(f"{TARGET_URL}/health", timeout=2)
            count += 1
        except:
            pass
        time.sleep(3)
    
    log(f"Benign traffic complete. Total: {count} requests", "SUCCESS")

def main():
    """Run gentle attack simulation."""
    print("\n" + "="*70)
    print(" "*15 + "GENTLE ATTACK SIMULATOR")
    print("="*70)
    print(f"Target: {TARGET_URL}")
    print("="*70 + "\n")
    
    # Check target
    try:
        response = requests.get(f"{TARGET_URL}/health", timeout=5)
        log(f"Target reachable! Status: {response.status_code}", "SUCCESS")
    except Exception as e:
        log(f"Cannot reach target: {e}", "ERROR")
        return
    
    attack_type = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    try:
        if attack_type == "benign":
            benign_traffic(30)
        elif attack_type == "ddos":
            gentle_ddos(30, rate=20)  # 20 requests/second
        elif attack_type == "web":
            web_attacks()
        else:  # all
            log("Running all attacks...", "INFO")
            benign_traffic(20)
            time.sleep(3)
            gentle_ddos(30, rate=15)
            time.sleep(3)
            web_attacks()
    
    except KeyboardInterrupt:
        log("Interrupted by user", "WARNING")
    
    print("\n" + "="*70)
    log("SIMULATION COMPLETE!", "SUCCESS")
    log("Check dashboard: http://localhost:5173", "INFO")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
