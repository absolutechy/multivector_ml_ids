// Statistics Dashboard Component
import { useEffect, useState } from 'react';
import type { Statistics } from '../services/api';
import { apiClient } from '../services/api';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const COLORS = {
  'Benign': '#10b981',
  'DDoS': '#ef4444',
  'Brute Force': '#f59e0b',
  'Web Attack': '#8b5cf6'
};

export const StatisticsDashboard = ({ statistics }: { statistics: Statistics | null }) => {
  const [localStats, setLocalStats] = useState<Statistics | null>(statistics);

  useEffect(() => {
    if (statistics) {
      setLocalStats(statistics);
    }
  }, [statistics]);

  useEffect(() => {
    // Fetch initial statistics
    const fetchStats = async () => {
      try {
        const stats = await apiClient.getStatistics();
        setLocalStats(stats);
      } catch (error) {
        console.error('Error fetching statistics:', error);
      }
    };

    if (!statistics) {
      fetchStats();
    }

    // Refresh every 10 seconds
    const interval = setInterval(fetchStats, 10000);
    return () => clearInterval(interval);
  }, [statistics]);

  if (!localStats) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <p className="text-gray-400">Loading statistics...</p>
      </div>
    );
  }

  // Prepare data for pie chart
  const pieData = Object.entries(localStats.attack_distribution).map(([name, data]) => ({
    name,
    value: data.count,
    percentage: data.percentage
  }));

  // Format uptime
  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    return `${hours}h ${minutes}m ${secs}s`;
  };

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white">
          <div className="text-sm font-medium opacity-90">Total Predictions</div>
          <div className="text-3xl font-bold mt-2">{localStats.total_predictions.toLocaleString()}</div>
        </div>

        <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-lg p-6 text-white">
          <div className="text-sm font-medium opacity-90">Detection Rate</div>
          <div className="text-3xl font-bold mt-2">{localStats.detection_rate.toFixed(1)}%</div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-6 text-white">
          <div className="text-sm font-medium opacity-90">Alerts in Memory</div>
          <div className="text-3xl font-bold mt-2">{localStats.alerts_in_memory}</div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-6 text-white">
          <div className="text-sm font-medium opacity-90">Uptime</div>
          <div className="text-2xl font-bold mt-2">{formatUptime(localStats.uptime_seconds)}</div>
        </div>
      </div>

      {/* Attack Distribution Chart */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-4">Attack Distribution</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={(props) => `${props.name}: ${props.payload.percentage.toFixed(1)}%`}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {pieData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[entry.name as keyof typeof COLORS] || '#6b7280'} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Attack Type Breakdown */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-4">Attack Type Breakdown</h3>
        <div className="space-y-3">
          {Object.entries(localStats.attack_distribution).map(([attackType, data]) => (
            <div key={attackType} className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div 
                  className="w-4 h-4 rounded"
                  style={{ backgroundColor: COLORS[attackType as keyof typeof COLORS] || '#6b7280' }}
                />
                <span className="text-white font-medium">{attackType}</span>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-gray-400">{data.count.toLocaleString()}</span>
                <span className="text-white font-semibold w-16 text-right">{data.percentage.toFixed(1)}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
