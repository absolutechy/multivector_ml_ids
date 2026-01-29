// Live Capture Control Component
import { useEffect, useState } from 'react';
import type { NetworkInterface, CaptureStatus } from '../services/api';
import { apiClient } from '../services/api';

export const LiveCaptureControl = () => {
  const [interfaces, setInterfaces] = useState<NetworkInterface[]>([]);
  const [selectedInterface, setSelectedInterface] = useState<number | null>(null);
  const [captureStatus, setCaptureStatus] = useState<CaptureStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchInterfaces();
    fetchStatus();

    // Poll status every 5 seconds
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchInterfaces = async () => {
    try {
      const response = await apiClient.listInterfaces();
      setInterfaces(response.interfaces);
      if (response.interfaces.length > 0 && !selectedInterface) {
        setSelectedInterface(response.interfaces[0].index);
      }
    } catch (error) {
      console.error('Error fetching interfaces:', error);
    }
  };

  const fetchStatus = async () => {
    try {
      const status = await apiClient.getCaptureStatus();
      setCaptureStatus(status);
    } catch (error) {
      console.error('Error fetching status:', error);
    }
  };

  const handleStart = async () => {
    if (!selectedInterface) {
      alert('Please select a network interface');
      return;
    }

    setIsLoading(true);
    try {
      await apiClient.startCapture(selectedInterface);
      await fetchStatus();
    } catch (error: any) {
      alert(`Error starting capture: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStop = async () => {
    setIsLoading(true);
    try {
      await apiClient.stopCapture();
      await fetchStatus();
    } catch (error: any) {
      alert(`Error stopping capture: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const isCapturing = captureStatus?.is_running || false;

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h3 className="text-xl font-semibold text-white mb-4">Live Capture Control</h3>

      {/* Model Status */}
      <div className="mb-4 p-3 rounded-lg bg-gray-700">
        <div className="flex items-center justify-between">
          <span className="text-gray-300">Model Status:</span>
          <span className={`font-semibold ${captureStatus?.model_loaded ? 'text-green-400' : 'text-red-400'}`}>
            {captureStatus?.model_loaded ? '✓ Loaded' : '✗ Not Loaded'}
          </span>
        </div>
      </div>

      {/* Interface Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Network Interface
        </label>
        <select
          value={selectedInterface || ''}
          onChange={(e) => setSelectedInterface(Number(e.target.value))}
          disabled={isCapturing}
          className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:border-blue-500 disabled:opacity-50"
        >
          <option value="">Select Interface</option>
          {interfaces.map((iface) => (
            <option key={iface.index} value={iface.index}>
              {iface.index}. {iface.name}
            </option>
          ))}
        </select>
      </div>

      {/* Control Buttons */}
      <div className="flex space-x-3 mb-4">
        <button
          onClick={handleStart}
          disabled={isCapturing || isLoading || !captureStatus?.model_loaded}
          className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-colors"
        >
          {isLoading ? 'Starting...' : '▶ Start Capture'}
        </button>

        <button
          onClick={handleStop}
          disabled={!isCapturing || isLoading}
          className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-colors"
        >
          {isLoading ? 'Stopping...' : '⏹ Stop Capture'}
        </button>
      </div>

      {/* Status Information */}
      {captureStatus && (
        <div className="space-y-2 p-4 bg-gray-700 rounded-lg">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-300">Status:</span>
            <span className={`font-semibold ${isCapturing ? 'text-green-400' : 'text-gray-400'}`}>
              {isCapturing ? '🟢 Capturing' : '⚪ Stopped'}
            </span>
          </div>

          {isCapturing && (
            <>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-300">Interface:</span>
                <span className="text-white font-mono">{captureStatus.capture.interface}</span>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-300">Packets Captured:</span>
                <span className="text-white font-semibold">{captureStatus.capture.total_packets.toLocaleString()}</span>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-300">Active Flows:</span>
                <span className="text-white font-semibold">{captureStatus.capture.active_flows}</span>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-300">Completed Flows:</span>
                <span className="text-white font-semibold">{captureStatus.capture.completed_flows}</span>
              </div>
            </>
          )}
        </div>
      )}

      {/* Warning */}
      {!captureStatus?.model_loaded && (
        <div className="mt-4 p-3 bg-yellow-500/10 border border-yellow-500 rounded-lg text-yellow-400 text-sm">
          ⚠ Model not loaded. Please train the model first: <code className="bg-gray-900 px-2 py-1 rounded">python scripts\train_pipeline.py</code>
        </div>
      )}

      {!isCapturing && (
        <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500 rounded-lg text-blue-400 text-sm">
          ℹ Note: Live capture requires Administrator privileges and Npcap driver on Windows.
        </div>
      )}
    </div>
  );
};
