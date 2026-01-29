// Alert Feed Component
import { useEffect, useState } from 'react';
import type { Alert } from '../services/api';
import { apiClient } from '../services/api';

interface AlertFeedProps {
  latestAlert: Alert | null;
}

export const AlertFeed = ({ latestAlert }: AlertFeedProps) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    // Fetch initial alerts
    const fetchAlerts = async () => {
      try {
        const response = await apiClient.getAlerts(50);
        setAlerts(response.alerts);
      } catch (error) {
        console.error('Error fetching alerts:', error);
      }
    };

    fetchAlerts();
  }, []);

  useEffect(() => {
    // Add new alert to the list
    if (latestAlert) {
      setAlerts(prev => [latestAlert, ...prev].slice(0, 100));
    }
  }, [latestAlert]);

  const getAlertColor = (attackType: string) => {
    switch (attackType) {
      case 'Benign':
        return 'bg-green-500/10 border-green-500 text-green-400';
      case 'DDoS':
        return 'bg-red-500/10 border-red-500 text-red-400';
      case 'Brute Force':
        return 'bg-yellow-500/10 border-yellow-500 text-yellow-400';
      case 'SQL Injection':
        return 'bg-purple-500/10 border-purple-500 text-purple-400';
      default:
        return 'bg-gray-500/10 border-gray-500 text-gray-400';
    }
  };

  const getAlertIcon = (attackType: string) => {
    if (attackType === 'Benign') return '✓';
    return '⚠';
  };

  const filteredAlerts = filter === 'all' 
    ? alerts 
    : alerts.filter(a => a.attack_type === filter);

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };

  const formatFlowKey = (flowKey: [string, string, number, number, number] | null) => {
    if (!flowKey) return 'N/A';
    const [srcIp, dstIp, srcPort, dstPort] = flowKey;
    return `${srcIp}:${srcPort} → ${dstIp}:${dstPort}`;
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold text-white">Real-Time Alerts</h3>
        
        {/* Filter */}
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:border-blue-500"
        >
          <option value="all">All Alerts</option>
          <option value="Benign">Benign</option>
          <option value="DDoS">DDoS</option>
          <option value="Brute Force">Brute Force</option>
          <option value="SQL Injection">SQL Injection</option>
        </select>
      </div>

      {/* Alert List */}
      <div className="space-y-2 max-h-[600px] overflow-y-auto">
        {filteredAlerts.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            No alerts yet. Start live capture to see real-time detections.
          </div>
        ) : (
          filteredAlerts.map((alert) => (
            <div
              key={alert.id}
              className={`border-l-4 p-4 rounded-r-lg ${getAlertColor(alert.attack_type)} transition-all duration-300 hover:shadow-lg`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  <span className="text-2xl">{getAlertIcon(alert.attack_type)}</span>
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold">{alert.attack_type}</span>
                      <span className="text-sm opacity-75">
                        {(alert.confidence * 100).toFixed(1)}% confidence
                      </span>
                    </div>
                    <div className="text-sm opacity-75 mt-1">
                      {formatFlowKey(alert.flow_key)}
                    </div>
                  </div>
                </div>
                <span className="text-xs opacity-60">{formatTimestamp(alert.timestamp)}</span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Alert Count */}
      <div className="mt-4 pt-4 border-t border-gray-700 text-sm text-gray-400">
        Showing {filteredAlerts.length} of {alerts.length} alerts
      </div>
    </div>
  );
};
