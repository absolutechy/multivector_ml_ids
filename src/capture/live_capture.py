"""
Live Network Interface Capture (PRIMARY)
Captures live packets from network interfaces using Scapy.
Requires administrator privileges and Npcap driver on Windows.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from scapy.all import sniff, get_if_list, conf
from collections import defaultdict, deque
import threading
import time
from datetime import datetime
import queue

from config.config import PACKET_BUFFER_SIZE, FLOW_TIMEOUT


class LiveCapture:
    """Live network packet capture and flow aggregation."""
    
    def __init__(self):
        self.interface = None
        self.is_capturing = False
        self.capture_thread = None
        self.packet_queue = queue.Queue(maxsize=PACKET_BUFFER_SIZE)
        self.flow_table = defaultdict(lambda: {
            'packets': [],
            'start_time': None,
            'last_seen': None
        })
        self.flows_ready = deque(maxlen=1000)  # Completed flows ready for prediction
        self.total_packets_captured = 0
        self.lock = threading.Lock()
        
    @staticmethod
    def list_interfaces():
        """
        List available network interfaces.
        
        Returns:
            List of interface names
        """
        try:
            interfaces = get_if_list()
            print("\nAvailable Network Interfaces:")
            print("-" * 60)
            for i, iface in enumerate(interfaces, 1):
                print(f"  {i}. {iface}")
            print("-" * 60)
            return interfaces
        except Exception as e:
            print(f"Error listing interfaces: {e}")
            print("\nNote: On Windows, you need:")
            print("  1. Npcap driver installed")
            print("  2. Run as Administrator")
            return []
    
    def select_interface(self, interface_name=None, interface_index=None):
        """
        Select network interface for capture.
        
        Args:
            interface_name: Name of interface (e.g., "Ethernet")
            interface_index: Index from list_interfaces() (1-based)
        """
        interfaces = get_if_list()
        
        if interface_index is not None:
            if 1 <= interface_index <= len(interfaces):
                self.interface = interfaces[interface_index - 1]
            else:
                raise ValueError(f"Invalid interface index. Must be 1-{len(interfaces)}")
        elif interface_name is not None:
            if interface_name in interfaces:
                self.interface = interface_name
            else:
                raise ValueError(f"Interface '{interface_name}' not found")
        else:
            # Use default interface
            self.interface = conf.iface
        
        print(f"\n✓ Selected interface: {self.interface}")
    
    def _packet_callback(self, packet):
        """
        Callback function for each captured packet.
        
        Args:
            packet: Scapy packet object
        """
        try:
            # Put packet in queue for processing
            if not self.packet_queue.full():
                self.packet_queue.put(packet)
                with self.lock:
                    self.total_packets_captured += 1
        except Exception as e:
            print(f"Error in packet callback: {e}")
    
    def _process_packets(self):
        """Process packets from queue and aggregate into flows."""
        while self.is_capturing or not self.packet_queue.empty():
            try:
                # Get packet from queue with timeout
                packet = self.packet_queue.get(timeout=1)
                
                # Extract flow key (5-tuple)
                flow_key = self._extract_flow_key(packet)
                if flow_key is None:
                    continue
                
                # Update flow table
                with self.lock:
                    flow = self.flow_table[flow_key]
                    
                    if flow['start_time'] is None:
                        flow['start_time'] = time.time()
                    
                    flow['last_seen'] = time.time()
                    flow['packets'].append(packet)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing packet: {e}")
        
        print("Packet processing thread stopped")
    
    def _extract_flow_key(self, packet):
        """
        Extract 5-tuple flow key from packet.
        
        Args:
            packet: Scapy packet
            
        Returns:
            Tuple of (src_ip, dst_ip, src_port, dst_port, protocol) or None
        """
        try:
            # Check if packet has IP layer
            if packet.haslayer('IP'):
                src_ip = packet['IP'].src
                dst_ip = packet['IP'].dst
                
                # Get protocol
                protocol = packet['IP'].proto
                
                # Get ports if TCP or UDP
                src_port = 0
                dst_port = 0
                
                if packet.haslayer('TCP'):
                    src_port = packet['TCP'].sport
                    dst_port = packet['TCP'].dport
                elif packet.haslayer('UDP'):
                    src_port = packet['UDP'].sport
                    dst_port = packet['UDP'].dport
                
                # Create bidirectional flow key (sort to ensure same key for both directions)
                if (src_ip, src_port) < (dst_ip, dst_port):
                    return (src_ip, dst_ip, src_port, dst_port, protocol)
                else:
                    return (dst_ip, src_ip, dst_port, src_port, protocol)
            
            return None
        except Exception as e:
            return None
    
    def _flow_timeout_checker(self):
        """Check for timed-out flows and move them to ready queue."""
        while self.is_capturing:
            try:
                current_time = time.time()
                flows_to_remove = []
                
                with self.lock:
                    for flow_key, flow_data in self.flow_table.items():
                        if flow_data['last_seen'] is not None:
                            time_since_last_packet = current_time - flow_data['last_seen']
                            
                            # If flow has timed out, mark for completion
                            if time_since_last_packet > FLOW_TIMEOUT:
                                # Add to ready queue
                                self.flows_ready.append({
                                    'flow_key': flow_key,
                                    'packets': flow_data['packets'].copy(),
                                    'start_time': flow_data['start_time'],
                                    'end_time': flow_data['last_seen']
                                })
                                flows_to_remove.append(flow_key)
                    
                    # Remove completed flows
                    for flow_key in flows_to_remove:
                        del self.flow_table[flow_key]
                
                # Sleep before next check
                time.sleep(10)
                
            except Exception as e:
                print(f"Error in flow timeout checker: {e}")
        
        print("Flow timeout checker stopped")
    
    def start_capture(self, packet_count=0, duration=0, filter_str=None):
        """
        Start live packet capture.
        
        Args:
            packet_count: Number of packets to capture (0 = unlimited)
            duration: Duration in seconds (0 = unlimited)
            filter_str: BPF filter string (e.g., "tcp port 80")
        """
        if self.interface is None:
            raise ValueError("No interface selected. Call select_interface() first.")
        
        if self.is_capturing:
            print("Capture already in progress")
            return
        
        print("\n" + "="*60)
        print("STARTING LIVE PACKET CAPTURE")
        print("="*60)
        print(f"Interface: {self.interface}")
        print(f"Filter: {filter_str if filter_str else 'None (all traffic)'}")
        print(f"Packet count: {packet_count if packet_count > 0 else 'Unlimited'}")
        print(f"Duration: {duration}s" if duration > 0 else "Duration: Unlimited")
        print("\nPress Ctrl+C to stop capture")
        print("="*60 + "\n")
        
        self.is_capturing = True
        
        # Start packet processing thread
        processing_thread = threading.Thread(target=self._process_packets, daemon=True)
        processing_thread.start()
        
        # Start flow timeout checker thread
        timeout_thread = threading.Thread(target=self._flow_timeout_checker, daemon=True)
        timeout_thread.start()
        
        # Start capture in separate thread
        def capture_worker():
            try:
                sniff(
                    iface=self.interface,
                    prn=self._packet_callback,
                    count=packet_count if packet_count > 0 else 0,
                    timeout=duration if duration > 0 else None,
                    filter=filter_str,
                    store=False  # Don't store packets in memory
                )
            except Exception as e:
                print(f"\nCapture error: {e}")
                print("\nCommon issues:")
                print("  1. Not running as Administrator")
                print("  2. Npcap not installed")
                print("  3. Invalid interface name")
            finally:
                self.is_capturing = False
        
        self.capture_thread = threading.Thread(target=capture_worker, daemon=True)
        self.capture_thread.start()
        
        print(f"✓ Capture started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def stop_capture(self):
        """Stop packet capture."""
        if not self.is_capturing:
            print("No capture in progress")
            return
        
        print("\nStopping capture...")
        self.is_capturing = False
        
        # Wait for capture thread to finish
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=5)
        
        print(f"✓ Capture stopped")
        print(f"Total packets captured: {self.total_packets_captured:,}")
        print(f"Active flows: {len(self.flow_table)}")
        print(f"Completed flows: {len(self.flows_ready)}")
    
    def get_capture_status(self):
        """
        Get current capture status.
        
        Returns:
            Dictionary with status information
        """
        with self.lock:
            return {
                'is_capturing': self.is_capturing,
                'interface': self.interface,
                'total_packets': self.total_packets_captured,
                'active_flows': len(self.flow_table),
                'completed_flows': len(self.flows_ready),
                'queue_size': self.packet_queue.qsize()
            }
    
    def get_completed_flows(self, max_flows=10):
        """
        Get completed flows ready for prediction.
        
        Args:
            max_flows: Maximum number of flows to return
            
        Returns:
            List of completed flow dictionaries
        """
        flows = []
        with self.lock:
            for _ in range(min(max_flows, len(self.flows_ready))):
                if self.flows_ready:
                    flows.append(self.flows_ready.popleft())
        return flows


def main():
    """Demonstrate live capture."""
    print("Live Network Capture Demo")
    print("="*60)
    
    # List interfaces
    capture = LiveCapture()
    interfaces = capture.list_interfaces()
    
    if not interfaces:
        print("\n❌ No interfaces found. Make sure:")
        print("  1. Npcap is installed")
        print("  2. Running as Administrator")
        return
    
    # Select interface (use first one or specify)
    try:
        capture.select_interface(interface_index=1)
    except Exception as e:
        print(f"Error selecting interface: {e}")
        return
    
    # Start capture for 30 seconds
    try:
        capture.start_capture(duration=30)
        
        # Monitor status
        while capture.is_capturing:
            time.sleep(5)
            status = capture.get_capture_status()
            print(f"\rPackets: {status['total_packets']:,} | "
                  f"Active flows: {status['active_flows']} | "
                  f"Completed: {status['completed_flows']}", end='')
        
        print("\n")
        
        # Get completed flows
        flows = capture.get_completed_flows(max_flows=5)
        print(f"\nSample completed flows: {len(flows)}")
        for i, flow in enumerate(flows, 1):
            print(f"\n  Flow {i}:")
            print(f"    5-tuple: {flow['flow_key']}")
            print(f"    Packets: {len(flow['packets'])}")
            print(f"    Duration: {flow['end_time'] - flow['start_time']:.2f}s")
        
    except KeyboardInterrupt:
        print("\n\nCapture interrupted by user")
        capture.stop_capture()
    except Exception as e:
        print(f"\nError: {e}")
        capture.stop_capture()


if __name__ == "__main__":
    main()
