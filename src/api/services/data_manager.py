"""
In-Memory Data Manager
Manages alerts and statistics using in-memory data structures with CSV logging.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from collections import deque
from datetime import datetime
import csv
import threading
from config.config import MAX_ALERTS_IN_MEMORY, CSV_EXPORT_DIR


class DataManager:
    """Manage alerts and statistics in memory with CSV export."""
    
    def __init__(self):
        self.alerts = deque(maxlen=MAX_ALERTS_IN_MEMORY)
        self.statistics = {
            'total_predictions': 0,
            'attack_counts': {
                'Benign': 0,
                'DDoS': 0,
                'Brute Force': 0,
                'SQL Injection': 0
            },
            'hourly_rates': deque(maxlen=24),  # Last 24 hours
            'start_time': datetime.now()
        }
        self.lock = threading.Lock()
        
        # Ensure export directory exists
        CSV_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        
    def add_alert(self, prediction_result):
        """
        Add a new alert/prediction.
        
        Args:
            prediction_result: Dictionary with prediction information
        """
        with self.lock:
            # Generate unique ID using timestamp + counter
            timestamp = datetime.now()
            unique_id = f"{int(timestamp.timestamp() * 1000)}-{self.statistics['total_predictions']}"
            
            # Add to alerts deque
            alert = {
                'id': unique_id,
                'timestamp': prediction_result.get('timestamp', timestamp.isoformat()),
                'attack_type': prediction_result.get('attack_type', 'Unknown'),
                'confidence': prediction_result.get('confidence', 0.0),
                'flow_key': prediction_result.get('flow_key'),
                'is_attack': prediction_result.get('is_attack', False)
            }
            
            self.alerts.append(alert)
            
            # Update statistics
            self.statistics['total_predictions'] += 1
            attack_type = alert['attack_type']
            if attack_type in self.statistics['attack_counts']:
                self.statistics['attack_counts'][attack_type] += 1
            
            # Log to CSV
            self._log_to_csv(alert)
            
            return alert
    
    def get_recent_alerts(self, limit=100, attack_type=None):
        """
        Get recent alerts.
        
        Args:
            limit: Maximum number of alerts to return
            attack_type: Filter by attack type (optional)
            
        Returns:
            List of alerts
        """
        with self.lock:
            alerts_list = list(self.alerts)
            
            # Filter by attack type if specified
            if attack_type:
                alerts_list = [a for a in alerts_list if a['attack_type'] == attack_type]
            
            # Return most recent first
            return alerts_list[-limit:][::-1]
    
    def get_statistics(self):
        """
        Get current statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self.lock:
            total = self.statistics['total_predictions']
            
            # Calculate percentages
            attack_distribution = {}
            for attack_type, count in self.statistics['attack_counts'].items():
                percentage = (count / total * 100) if total > 0 else 0
                attack_distribution[attack_type] = {
                    'count': count,
                    'percentage': round(percentage, 2)
                }
            
            # Calculate detection rate
            attacks_detected = total - self.statistics['attack_counts'].get('Benign', 0)
            detection_rate = (attacks_detected / total * 100) if total > 0 else 0
            
            # Calculate uptime
            uptime_seconds = (datetime.now() - self.statistics['start_time']).total_seconds()
            
            return {
                'total_predictions': total,
                'attack_distribution': attack_distribution,
                'detection_rate': round(detection_rate, 2),
                'uptime_seconds': round(uptime_seconds, 2),
                'alerts_in_memory': len(self.alerts)
            }
    
    def _log_to_csv(self, alert):
        """
        Log alert to CSV file.
        
        Args:
            alert: Alert dictionary
        """
        try:
            # Create daily CSV file
            date_str = datetime.now().strftime('%Y-%m-%d')
            csv_file = CSV_EXPORT_DIR / f"alerts_{date_str}.csv"
            
            # Check if file exists
            file_exists = csv_file.exists()
            
            # Write to CSV
            with open(csv_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'id', 'timestamp', 'attack_type', 'confidence', 
                    'src_ip', 'dst_ip', 'src_port', 'dst_port', 'protocol', 'is_attack'
                ])
                
                # Write header if new file
                if not file_exists:
                    writer.writeheader()
                
                # Extract flow key if available
                flow_key = alert.get('flow_key')
                if flow_key and len(flow_key) == 5:
                    src_ip, dst_ip, src_port, dst_port, protocol = flow_key
                else:
                    src_ip = dst_ip = src_port = dst_port = protocol = None
                
                # Write row
                writer.writerow({
                    'id': alert['id'],
                    'timestamp': alert['timestamp'],
                    'attack_type': alert['attack_type'],
                    'confidence': alert['confidence'],
                    'src_ip': src_ip,
                    'dst_ip': dst_ip,
                    'src_port': src_port,
                    'dst_port': dst_port,
                    'protocol': protocol,
                    'is_attack': alert['is_attack']
                })
                
        except Exception as e:
            print(f"Error logging to CSV: {e}")
    
    def export_all_alerts_to_csv(self, output_file=None):
        """
        Export all in-memory alerts to a single CSV file.
        
        Args:
            output_file: Path to output file (default: exports/all_alerts.csv)
            
        Returns:
            Path to exported file
        """
        if output_file is None:
            output_file = CSV_EXPORT_DIR / "all_alerts.csv"
        else:
            output_file = Path(output_file)
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with self.lock:
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'id', 'timestamp', 'attack_type', 'confidence', 
                    'src_ip', 'dst_ip', 'src_port', 'dst_port', 'protocol', 'is_attack'
                ])
                
                writer.writeheader()
                
                for alert in self.alerts:
                    flow_key = alert.get('flow_key')
                    if flow_key and len(flow_key) == 5:
                        src_ip, dst_ip, src_port, dst_port, protocol = flow_key
                    else:
                        src_ip = dst_ip = src_port = dst_port = protocol = None
                    
                    writer.writerow({
                        'id': alert['id'],
                        'timestamp': alert['timestamp'],
                        'attack_type': alert['attack_type'],
                        'confidence': alert['confidence'],
                        'src_ip': src_ip,
                        'dst_ip': dst_ip,
                        'src_port': src_port,
                        'dst_port': dst_port,
                        'protocol': protocol,
                        'is_attack': alert['is_attack']
                    })
        
        print(f"✓ Exported {len(self.alerts)} alerts to {output_file}")
        return str(output_file)
    
    def clear_alerts(self):
        """Clear all alerts from memory."""
        with self.lock:
            self.alerts.clear()
            print("✓ Alerts cleared from memory")
    
    def reset_statistics(self):
        """Reset statistics."""
        with self.lock:
            self.statistics = {
                'total_predictions': 0,
                'attack_counts': {
                    'Benign': 0,
                    'DDoS': 0,
                    'Brute Force': 0,
                    'SQL Injection': 0
                },
                'hourly_rates': deque(maxlen=24),
                'start_time': datetime.now()
            }
            print("✓ Statistics reset")


# Global data manager instance
data_manager = DataManager()


def main():
    """Demonstrate data manager."""
    print("Data Manager Demo")
    print("="*60)
    
    # Add some dummy alerts
    for i in range(10):
        result = {
            'timestamp': datetime.now().isoformat(),
            'attack_type': ['Benign', 'DDoS', 'Brute Force', 'SQL Injection'][i % 4],
            'confidence': 0.85 + (i % 10) / 100,
            'flow_key': ('192.168.1.1', '8.8.8.8', 12345 + i, 80, 6),
            'is_attack': i % 4 != 0
        }
        data_manager.add_alert(result)
    
    # Get statistics
    stats = data_manager.get_statistics()
    print("\nStatistics:")
    print(f"  Total predictions: {stats['total_predictions']}")
    print(f"  Detection rate: {stats['detection_rate']}%")
    print(f"\n  Attack distribution:")
    for attack_type, info in stats['attack_distribution'].items():
        print(f"    {attack_type:20s}: {info['count']:3d} ({info['percentage']:5.1f}%)")
    
    # Get recent alerts
    recent = data_manager.get_recent_alerts(limit=5)
    print(f"\nRecent alerts ({len(recent)}):")
    for alert in recent:
        print(f"  {alert['id']:3d}. {alert['attack_type']:20s} ({alert['confidence']*100:.1f}%)")
    
    # Export
    export_file = data_manager.export_all_alerts_to_csv()
    print(f"\nExported to: {export_file}")


if __name__ == "__main__":
    main()
