"""
PCAP File Parser (SECONDARY - for forensic analysis)
Parses pre-captured PCAP files using Scapy and pyshark.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from scapy.all import rdpcap, PcapReader
from collections import defaultdict
import time


class PcapParser:
    """Parse PCAP files and extract flows."""
    
    def __init__(self, pcap_file):
        """
        Initialize PCAP parser.
        
        Args:
            pcap_file: Path to PCAP file
        """
        self.pcap_file = Path(pcap_file)
        if not self.pcap_file.exists():
            raise FileNotFoundError(f"PCAP file not found: {pcap_file}")
        
        self.flows = defaultdict(lambda: {
            'packets': [],
            'start_time': None,
            'end_time': None
        })
        self.total_packets = 0
        
    def parse_pcap(self, max_packets=None):
        """
        Parse PCAP file and extract flows.
        
        Args:
            max_packets: Maximum number of packets to read (None = all)
        """
        print(f"\nParsing PCAP file: {self.pcap_file.name}")
        print("-" * 60)
        
        start_time = time.time()
        
        try:
            # Use PcapReader for memory efficiency with large files
            with PcapReader(str(self.pcap_file)) as pcap_reader:
                for i, packet in enumerate(pcap_reader):
                    if max_packets and i >= max_packets:
                        break
                    
                    # Extract flow key
                    flow_key = self._extract_flow_key(packet)
                    if flow_key is None:
                        continue
                    
                    # Get packet timestamp
                    pkt_time = float(packet.time) if hasattr(packet, 'time') else time.time()
                    
                    # Update flow
                    flow = self.flows[flow_key]
                    
                    if flow['start_time'] is None:
                        flow['start_time'] = pkt_time
                    
                    flow['end_time'] = pkt_time
                    flow['packets'].append(packet)
                    
                    self.total_packets += 1
                    
                    # Progress indicator
                    if (i + 1) % 10000 == 0:
                        print(f"  Processed {i+1:,} packets...", end='\r')
            
            parse_time = time.time() - start_time
            
            print(f"\n✓ Parsing complete")
            print(f"  Total packets: {self.total_packets:,}")
            print(f"  Total flows: {len(self.flows):,}")
            print(f"  Parse time: {parse_time:.2f}s")
            print(f"  Rate: {self.total_packets/parse_time:.0f} packets/sec")
            print("-" * 60)
            
        except Exception as e:
            print(f"\n❌ Error parsing PCAP: {e}")
            raise
    
    def _extract_flow_key(self, packet):
        """
        Extract 5-tuple flow key from packet.
        
        Args:
            packet: Scapy packet
            
        Returns:
            Tuple of (src_ip, dst_ip, src_port, dst_port, protocol) or None
        """
        try:
            if packet.haslayer('IP'):
                src_ip = packet['IP'].src
                dst_ip = packet['IP'].dst
                protocol = packet['IP'].proto
                
                src_port = 0
                dst_port = 0
                
                if packet.haslayer('TCP'):
                    src_port = packet['TCP'].sport
                    dst_port = packet['TCP'].dport
                elif packet.haslayer('UDP'):
                    src_port = packet['UDP'].sport
                    dst_port = packet['UDP'].dport
                
                # Bidirectional flow key
                if (src_ip, src_port) < (dst_ip, dst_port):
                    return (src_ip, dst_ip, src_port, dst_port, protocol)
                else:
                    return (dst_ip, src_ip, dst_port, src_port, protocol)
            
            return None
        except:
            return None
    
    def get_flows(self):
        """
        Get all extracted flows.
        
        Returns:
            Dictionary of flows
        """
        return dict(self.flows)
    
    def get_flow_summary(self):
        """
        Get summary statistics of flows.
        
        Returns:
            Dictionary with summary statistics
        """
        if not self.flows:
            return {}
        
        packet_counts = [len(flow['packets']) for flow in self.flows.values()]
        durations = [
            flow['end_time'] - flow['start_time'] 
            for flow in self.flows.values() 
            if flow['start_time'] and flow['end_time']
        ]
        
        return {
            'total_flows': len(self.flows),
            'total_packets': self.total_packets,
            'avg_packets_per_flow': sum(packet_counts) / len(packet_counts) if packet_counts else 0,
            'max_packets_per_flow': max(packet_counts) if packet_counts else 0,
            'min_packets_per_flow': min(packet_counts) if packet_counts else 0,
            'avg_flow_duration': sum(durations) / len(durations) if durations else 0,
            'max_flow_duration': max(durations) if durations else 0,
            'min_flow_duration': min(durations) if durations else 0
        }
    
    def export_flows_to_csv(self, output_file):
        """
        Export flow summary to CSV.
        
        Args:
            output_file: Path to output CSV file
        """
        import csv
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'src_ip', 'dst_ip', 'src_port', 'dst_port', 'protocol',
                'packet_count', 'duration', 'start_time', 'end_time'
            ])
            
            # Flows
            for flow_key, flow_data in self.flows.items():
                src_ip, dst_ip, src_port, dst_port, protocol = flow_key
                packet_count = len(flow_data['packets'])
                duration = flow_data['end_time'] - flow_data['start_time'] if flow_data['start_time'] else 0
                
                writer.writerow([
                    src_ip, dst_ip, src_port, dst_port, protocol,
                    packet_count, f"{duration:.3f}",
                    flow_data['start_time'], flow_data['end_time']
                ])
        
        print(f"✓ Flows exported to {output_path}")


def main():
    """Demonstrate PCAP parsing."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pcap_parser.py <pcap_file>")
        print("\nExample: python pcap_parser.py data/sample_pcaps/traffic.pcap")
        return
    
    pcap_file = sys.argv[1]
    
    try:
        # Parse PCAP
        parser = PcapParser(pcap_file)
        parser.parse_pcap()
        
        # Get summary
        summary = parser.get_flow_summary()
        
        print("\nFlow Summary:")
        print("-" * 60)
        print(f"  Total flows: {summary['total_flows']:,}")
        print(f"  Total packets: {summary['total_packets']:,}")
        print(f"  Avg packets/flow: {summary['avg_packets_per_flow']:.1f}")
        print(f"  Avg flow duration: {summary['avg_flow_duration']:.3f}s")
        print("-" * 60)
        
        # Export to CSV
        csv_file = Path(pcap_file).with_suffix('.csv')
        parser.export_flows_to_csv(csv_file)
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
