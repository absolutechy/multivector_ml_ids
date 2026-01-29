"""
Flow Feature Extractor
Converts raw packets to CICIDS2017-compatible features for ML prediction.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
from collections import defaultdict
import time


class FlowFeatureExtractor:
    """Extract CICIDS2017-compatible features from packet flows."""
    
    def __init__(self):
        self.feature_names = self._get_feature_names()
        
    def _get_feature_names(self):
        """
        Get list of CICIDS2017 feature names.
        Note: This is a simplified set. Full CICIDS2017 has 78 features.
        """
        return [
            # Basic flow features
            'flow_duration', 'total_fwd_packets', 'total_bwd_packets',
            'total_length_fwd_packets', 'total_length_bwd_packets',
            
            # Packet length statistics
            'fwd_packet_length_max', 'fwd_packet_length_min',
            'fwd_packet_length_mean', 'fwd_packet_length_std',
            'bwd_packet_length_max', 'bwd_packet_length_min',
            'bwd_packet_length_mean', 'bwd_packet_length_std',
            
            # Flow bytes/packets per second
            'flow_bytes_per_sec', 'flow_packets_per_sec',
            'flow_iat_mean', 'flow_iat_std', 'flow_iat_max', 'flow_iat_min',
            
            # Forward IAT
            'fwd_iat_total', 'fwd_iat_mean', 'fwd_iat_std',
            'fwd_iat_max', 'fwd_iat_min',
            
            # Backward IAT
            'bwd_iat_total', 'bwd_iat_mean', 'bwd_iat_std',
            'bwd_iat_max', 'bwd_iat_min',
            
            # Flags
            'fwd_psh_flags', 'bwd_psh_flags', 'fwd_urg_flags', 'bwd_urg_flags',
            'fwd_header_length', 'bwd_header_length',
            
            # Packets per second
            'fwd_packets_per_sec', 'bwd_packets_per_sec',
            
            # Packet length
            'min_packet_length', 'max_packet_length',
            'packet_length_mean', 'packet_length_std', 'packet_length_variance',
            
            # Flag counts
            'fin_flag_count', 'syn_flag_count', 'rst_flag_count',
            'psh_flag_count', 'ack_flag_count', 'urg_flag_count',
            'cwe_flag_count', 'ece_flag_count',
            
            # Down/Up ratio
            'down_up_ratio', 'avg_packet_size', 'avg_fwd_segment_size',
            'avg_bwd_segment_size',
            
            # Header lengths
            'fwd_header_length_total', 'bwd_header_length_total',
            
            # Subflow features
            'subflow_fwd_packets', 'subflow_fwd_bytes',
            'subflow_bwd_packets', 'subflow_bwd_bytes',
            
            # Init window size
            'init_win_bytes_forward', 'init_win_bytes_backward',
            
            # Active/Idle
            'act_data_pkt_fwd', 'min_seg_size_forward',
            
            # Additional timing
            'active_mean', 'active_std', 'active_max', 'active_min',
            'idle_mean', 'idle_std', 'idle_max', 'idle_min'
        ]
    
    def extract_features_from_flow(self, flow_data):
        """
        Extract features from a single flow.
        
        Args:
            flow_data: Dictionary with 'packets', 'start_time', 'end_time'
            
        Returns:
            Dictionary of features
        """
        packets = flow_data['packets']
        if not packets:
            return None
        
        # Separate forward and backward packets
        fwd_packets, bwd_packets = self._separate_directions(packets)
        
        # Calculate features
        features = {}
        
        # Flow duration
        duration = flow_data['end_time'] - flow_data['start_time'] if flow_data['start_time'] else 0
        features['flow_duration'] = duration * 1_000_000  # Convert to microseconds
        
        # Packet counts
        features['total_fwd_packets'] = len(fwd_packets)
        features['total_bwd_packets'] = len(bwd_packets)
        
        # Packet lengths
        fwd_lengths = [self._get_packet_length(p) for p in fwd_packets]
        bwd_lengths = [self._get_packet_length(p) for p in bwd_packets]
        all_lengths = fwd_lengths + bwd_lengths
        
        features['total_length_fwd_packets'] = sum(fwd_lengths)
        features['total_length_bwd_packets'] = sum(bwd_lengths)
        
        # Forward packet length statistics
        features['fwd_packet_length_max'] = max(fwd_lengths) if fwd_lengths else 0
        features['fwd_packet_length_min'] = min(fwd_lengths) if fwd_lengths else 0
        features['fwd_packet_length_mean'] = np.mean(fwd_lengths) if fwd_lengths else 0
        features['fwd_packet_length_std'] = np.std(fwd_lengths) if fwd_lengths else 0
        
        # Backward packet length statistics
        features['bwd_packet_length_max'] = max(bwd_lengths) if bwd_lengths else 0
        features['bwd_packet_length_min'] = min(bwd_lengths) if bwd_lengths else 0
        features['bwd_packet_length_mean'] = np.mean(bwd_lengths) if bwd_lengths else 0
        features['bwd_packet_length_std'] = np.std(bwd_lengths) if bwd_lengths else 0
        
        # Flow bytes/packets per second
        if duration > 0:
            features['flow_bytes_per_sec'] = sum(all_lengths) / duration
            features['flow_packets_per_sec'] = len(packets) / duration
            features['fwd_packets_per_sec'] = len(fwd_packets) / duration
            features['bwd_packets_per_sec'] = len(bwd_packets) / duration
        else:
            features['flow_bytes_per_sec'] = 0
            features['flow_packets_per_sec'] = 0
            features['fwd_packets_per_sec'] = 0
            features['bwd_packets_per_sec'] = 0
        
        # Inter-arrival times
        fwd_iats = self._calculate_iats(fwd_packets)
        bwd_iats = self._calculate_iats(bwd_packets)
        all_iats = self._calculate_iats(packets)
        
        # Flow IAT
        features['flow_iat_mean'] = np.mean(all_iats) if all_iats else 0
        features['flow_iat_std'] = np.std(all_iats) if all_iats else 0
        features['flow_iat_max'] = max(all_iats) if all_iats else 0
        features['flow_iat_min'] = min(all_iats) if all_iats else 0
        
        # Forward IAT
        features['fwd_iat_total'] = sum(fwd_iats) if fwd_iats else 0
        features['fwd_iat_mean'] = np.mean(fwd_iats) if fwd_iats else 0
        features['fwd_iat_std'] = np.std(fwd_iats) if fwd_iats else 0
        features['fwd_iat_max'] = max(fwd_iats) if fwd_iats else 0
        features['fwd_iat_min'] = min(fwd_iats) if fwd_iats else 0
        
        # Backward IAT
        features['bwd_iat_total'] = sum(bwd_iats) if bwd_iats else 0
        features['bwd_iat_mean'] = np.mean(bwd_iats) if bwd_iats else 0
        features['bwd_iat_std'] = np.std(bwd_iats) if bwd_iats else 0
        features['bwd_iat_max'] = max(bwd_iats) if bwd_iats else 0
        features['bwd_iat_min'] = min(bwd_iats) if bwd_iats else 0
        
        # TCP flags
        flag_counts = self._count_tcp_flags(packets)
        fwd_flags = self._count_tcp_flags(fwd_packets)
        bwd_flags = self._count_tcp_flags(bwd_packets)
        
        features['fwd_psh_flags'] = fwd_flags.get('PSH', 0)
        features['bwd_psh_flags'] = bwd_flags.get('PSH', 0)
        features['fwd_urg_flags'] = fwd_flags.get('URG', 0)
        features['bwd_urg_flags'] = bwd_flags.get('URG', 0)
        
        features['fin_flag_count'] = flag_counts.get('FIN', 0)
        features['syn_flag_count'] = flag_counts.get('SYN', 0)
        features['rst_flag_count'] = flag_counts.get('RST', 0)
        features['psh_flag_count'] = flag_counts.get('PSH', 0)
        features['ack_flag_count'] = flag_counts.get('ACK', 0)
        features['urg_flag_count'] = flag_counts.get('URG', 0)
        features['cwe_flag_count'] = flag_counts.get('CWR', 0)
        features['ece_flag_count'] = flag_counts.get('ECE', 0)
        
        # Header lengths
        fwd_header_lengths = [self._get_header_length(p) for p in fwd_packets]
        bwd_header_lengths = [self._get_header_length(p) for p in bwd_packets]
        
        features['fwd_header_length'] = np.mean(fwd_header_lengths) if fwd_header_lengths else 0
        features['bwd_header_length'] = np.mean(bwd_header_lengths) if bwd_header_lengths else 0
        features['fwd_header_length_total'] = sum(fwd_header_lengths)
        features['bwd_header_length_total'] = sum(bwd_header_lengths)
        
        # Packet length statistics
        features['min_packet_length'] = min(all_lengths) if all_lengths else 0
        features['max_packet_length'] = max(all_lengths) if all_lengths else 0
        features['packet_length_mean'] = np.mean(all_lengths) if all_lengths else 0
        features['packet_length_std'] = np.std(all_lengths) if all_lengths else 0
        features['packet_length_variance'] = np.var(all_lengths) if all_lengths else 0
        
        # Down/Up ratio
        if features['total_length_fwd_packets'] > 0:
            features['down_up_ratio'] = features['total_length_bwd_packets'] / features['total_length_fwd_packets']
        else:
            features['down_up_ratio'] = 0
        
        # Average sizes
        features['avg_packet_size'] = np.mean(all_lengths) if all_lengths else 0
        features['avg_fwd_segment_size'] = np.mean(fwd_lengths) if fwd_lengths else 0
        features['avg_bwd_segment_size'] = np.mean(bwd_lengths) if bwd_lengths else 0
        
        # Subflow features (simplified - using total flow)
        features['subflow_fwd_packets'] = len(fwd_packets)
        features['subflow_fwd_bytes'] = sum(fwd_lengths)
        features['subflow_bwd_packets'] = len(bwd_packets)
        features['subflow_bwd_bytes'] = sum(bwd_lengths)
        
        # Window sizes (simplified)
        features['init_win_bytes_forward'] = self._get_window_size(fwd_packets[0]) if fwd_packets else 0
        features['init_win_bytes_backward'] = self._get_window_size(bwd_packets[0]) if bwd_packets else 0
        
        # Active data packets
        features['act_data_pkt_fwd'] = len([p for p in fwd_packets if self._get_packet_length(p) > 0])
        features['min_seg_size_forward'] = min(fwd_lengths) if fwd_lengths else 0
        
        # Active/Idle times (simplified - set to 0 for now)
        features['active_mean'] = 0
        features['active_std'] = 0
        features['active_max'] = 0
        features['active_min'] = 0
        features['idle_mean'] = 0
        features['idle_std'] = 0
        features['idle_max'] = 0
        features['idle_min'] = 0
        
        return features
    
    def _separate_directions(self, packets):
        """Separate packets into forward and backward directions."""
        if not packets:
            return [], []
        
        # Use first packet to determine forward direction
        first_pkt = packets[0]
        if not first_pkt.haslayer('IP'):
            return packets, []
        
        fwd_ip = first_pkt['IP'].src
        fwd_port = first_pkt['TCP'].sport if first_pkt.haslayer('TCP') else (first_pkt['UDP'].sport if first_pkt.haslayer('UDP') else 0)
        
        fwd_packets = []
        bwd_packets = []
        
        for pkt in packets:
            if pkt.haslayer('IP'):
                if pkt['IP'].src == fwd_ip:
                    fwd_packets.append(pkt)
                else:
                    bwd_packets.append(pkt)
        
        return fwd_packets, bwd_packets
    
    def _get_packet_length(self, packet):
        """Get total packet length."""
        return len(packet) if packet else 0
    
    def _get_header_length(self, packet):
        """Get header length."""
        header_len = 0
        if packet.haslayer('IP'):
            header_len += packet['IP'].ihl * 4
        if packet.haslayer('TCP'):
            header_len += packet['TCP'].dataofs * 4
        elif packet.haslayer('UDP'):
            header_len += 8
        return header_len
    
    def _calculate_iats(self, packets):
        """Calculate inter-arrival times."""
        if len(packets) < 2:
            return []
        
        iats = []
        for i in range(1, len(packets)):
            if hasattr(packets[i], 'time') and hasattr(packets[i-1], 'time'):
                iat = (float(packets[i].time) - float(packets[i-1].time)) * 1_000_000  # microseconds
                iats.append(iat)
        
        return iats
    
    def _count_tcp_flags(self, packets):
        """Count TCP flags."""
        flags = defaultdict(int)
        
        for pkt in packets:
            if pkt.haslayer('TCP'):
                tcp_flags = pkt['TCP'].flags
                if tcp_flags.F: flags['FIN'] += 1
                if tcp_flags.S: flags['SYN'] += 1
                if tcp_flags.R: flags['RST'] += 1
                if tcp_flags.P: flags['PSH'] += 1
                if tcp_flags.A: flags['ACK'] += 1
                if tcp_flags.U: flags['URG'] += 1
                if tcp_flags.C: flags['CWR'] += 1
                if tcp_flags.E: flags['ECE'] += 1
        
        return dict(flags)
    
    def _get_window_size(self, packet):
        """Get TCP window size."""
        if packet and packet.haslayer('TCP'):
            return packet['TCP'].window
        return 0


def main():
    """Demonstrate feature extraction."""
    print("Flow Feature Extractor Demo")
    print("="*60)
    
    extractor = FlowFeatureExtractor()
    print(f"Total features: {len(extractor.feature_names)}")
    print(f"\nFeature names (first 10):")
    for i, name in enumerate(extractor.feature_names[:10], 1):
        print(f"  {i}. {name}")
    print("  ...")


if __name__ == "__main__":
    main()
