"""
Integrated Live Capture and Prediction Service
Combines live capture, feature extraction, and real-time prediction.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import threading
import time
from datetime import datetime

from src.capture.live_capture import LiveCapture
from src.inference.feature_extractor import FlowFeatureExtractor
from src.inference.predictor import Predictor
from src.api.services.data_manager import data_manager
from src.api.websocket.alert_handler import manager
import asyncio


class LiveDetectionService:
    """Integrated service for live capture and real-time detection."""
    
    def __init__(self):
        self.capture = LiveCapture()
        self.extractor = FlowFeatureExtractor()
        self.predictor = Predictor()
        self.is_running = False
        self.prediction_thread = None
        
    def start(self, interface_name=None, interface_index=None):
        """
        Start live detection service.
        
        Args:
            interface_name: Network interface name
            interface_index: Network interface index (1-based)
        """
        print("\n" + "="*60)
        print("STARTING LIVE DETECTION SERVICE")
        print("="*60)
        
        # Load model
        try:
            self.predictor.load_model_and_transformers()
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("  Run training pipeline first: python scripts/train_pipeline.py")
            return False
        
        # Select interface
        try:
            self.capture.select_interface(
                interface_name=interface_name,
                interface_index=interface_index
            )
        except Exception as e:
            print(f"❌ Error selecting interface: {e}")
            return False
        
        # Start capture
        self.capture.start_capture()
        
        # Start prediction thread
        self.is_running = True
        self.prediction_thread = threading.Thread(
            target=self._prediction_worker,
            daemon=True
        )
        self.prediction_thread.start()
        
        print("✓ Live detection service started")
        print("="*60 + "\n")
        
        return True
    
    def stop(self):
        """Stop live detection service."""
        print("\nStopping live detection service...")
        
        self.is_running = False
        self.capture.stop_capture()
        
        if self.prediction_thread and self.prediction_thread.is_alive():
            self.prediction_thread.join(timeout=5)
        
        print("✓ Live detection service stopped\n")
    
    def _prediction_worker(self):
        """Worker thread for processing flows and making predictions."""
        print("Prediction worker started")
        
        while self.is_running:
            try:
                # Get completed flows
                flows = self.capture.get_completed_flows(max_flows=10)
                
                if not flows:
                    time.sleep(1)
                    continue
                
                # Process each flow
                for flow_data in flows:
                    try:
                        # Extract features
                        features = self.extractor.extract_features_from_flow(flow_data)
                        
                        if features is None:
                            continue
                        
                        # Make prediction
                        result = self.predictor.predict_flow(
                            features,
                            flow_key=flow_data['flow_key']
                        )
                        
                        # Add to data manager
                        alert = data_manager.add_alert(result)
                        
                        # Broadcast via WebSocket (async)
                        asyncio.run(manager.broadcast_alert(alert))
                        
                        # Print if attack detected
                        if result['is_attack']:
                            print(f"\n🚨 ATTACK DETECTED!")
                            print(f"  Type: {result['attack_type']}")
                            print(f"  Confidence: {result['confidence']*100:.1f}%")
                            print(f"  Flow: {flow_data['flow_key']}")
                        
                    except Exception as e:
                        print(f"Error processing flow: {e}")
                
            except Exception as e:
                print(f"Error in prediction worker: {e}")
                time.sleep(1)
        
        print("Prediction worker stopped")
    
    def get_status(self):
        """Get service status."""
        capture_status = self.capture.get_capture_status()
        stats = data_manager.get_statistics()
        
        return {
            'is_running': self.is_running,
            'capture': capture_status,
            'statistics': stats,
            'model_loaded': self.predictor.is_loaded
        }


def main():
    """Demonstrate live detection service."""
    import signal
    
    service = LiveDetectionService()
    
    # List interfaces
    print("Available interfaces:")
    LiveCapture.list_interfaces()
    
    # Start service (use first interface)
    if not service.start(interface_index=1):
        print("Failed to start service")
        return
    
    # Handle Ctrl+C
    def signal_handler(sig, frame):
        print("\n\nReceived interrupt signal")
        service.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Monitor status
    try:
        while True:
            time.sleep(10)
            status = service.get_status()
            print(f"\rPackets: {status['capture']['total_packets']:,} | "
                  f"Predictions: {status['statistics']['total_predictions']:,} | "
                  f"Attacks: {status['statistics']['detection_rate']:.1f}%", end='')
    except KeyboardInterrupt:
        service.stop()


if __name__ == "__main__":
    main()
