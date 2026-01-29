// Main App Component
import { useState } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import { StatisticsDashboard } from './components/StatisticsDashboard';
import { AlertFeed } from './components/AlertFeed';
import { LiveCaptureControl } from './components/LiveCaptureControl';

function App() {
  const { isConnected, latestAlert, statistics } = useWebSocket();
  const [activeTab, setActiveTab] = useState<'dashboard' | 'alerts' | 'capture'>('dashboard');

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Header */}
      <header className="bg-gray-800/50 backdrop-blur-sm border-b border-gray-700 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">Multi-Vector IDS</h1>
              <p className="text-sm text-gray-400">Real-Time Intrusion Detection System</p>
            </div>

            {/* Connection Status */}
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
              <span className="text-sm text-gray-300">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="mt-4 flex space-x-1">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                activeTab === 'dashboard'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
            >
              📊 Dashboard
            </button>
            <button
              onClick={() => setActiveTab('alerts')}
              className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                activeTab === 'alerts'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
            >
              🚨 Alerts
            </button>
            <button
              onClick={() => setActiveTab('capture')}
              className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                activeTab === 'capture'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
            >
              📡 Live Capture
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {activeTab === 'dashboard' && (
          <StatisticsDashboard statistics={statistics} />
        )}

        {activeTab === 'alerts' && (
          <AlertFeed latestAlert={latestAlert} />
        )}

        {activeTab === 'capture' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1">
              <LiveCaptureControl />
            </div>
            <div className="lg:col-span-2">
              <AlertFeed latestAlert={latestAlert} />
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800/50 border-t border-gray-700 mt-12">
        <div className="container mx-auto px-6 py-4 text-center text-sm text-gray-400">
          <p>Multi-Vector Attack Detection System | Final Year Project 2026</p>
          <p className="mt-1">Random Forest Classifier | CICIDS2017 Dataset</p>
        </div>
      </footer>
    </div>
  );
}

export default App;