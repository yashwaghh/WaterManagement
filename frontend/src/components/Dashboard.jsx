import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Droplet, Settings } from 'lucide-react';
import apiService from '../services/api';
import useStore from '../store/useStore';
import LeaderboardTab from './tabs/LeaderboardTab';
import AnalyticsTab from './tabs/AnalyticsTab';
import AdminTab from './tabs/AdminTab';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('leaderboard');
  const [isConnected, setIsConnected] = useState(false);
  const { error, clearError } = useStore();

  // Check API connection on mount
  useEffect(() => {
    const checkConnection = async () => {
      try {
        await apiService.checkHealth();
        setIsConnected(true);
      } catch (err) {
        setIsConnected(false);
        console.error('Failed to connect to API:', err);
      }
    };

    checkConnection();
    const interval = setInterval(checkConnection, 10000); // Check every 10s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-primary-600 to-primary-700 rounded-lg">
                <Droplet className="text-white" size={24} />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Water Management</h1>
                <p className="text-sm text-gray-600">Multi-Flat Analytics & Ranking System</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div
                className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${
                  isConnected
                    ? 'bg-green-100 text-green-700'
                    : 'bg-red-100 text-red-700'
                }`}
              >
                <div
                  className={`w-2 h-2 rounded-full ${
                    isConnected ? 'bg-green-600 animate-pulse' : 'bg-red-600'
                  }`}
                />
                {isConnected ? 'Connected' : 'Disconnected'}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 border-b border-red-200 p-4">
          <div className="max-w-7xl mx-auto flex justify-between items-center">
            <p className="text-red-800">{error}</p>
            <button
              onClick={clearError}
              className="text-red-600 hover:text-red-800 font-medium"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Tab Navigation */}
        <div className="flex gap-2 mb-8 border-b border-gray-200 bg-white rounded-t-lg px-6 pt-4">
          <button
            onClick={() => setActiveTab('leaderboard')}
            className={`tab-button ${activeTab === 'leaderboard' ? 'active' : ''}`}
          >
            <div className="flex items-center gap-2">
              <BarChart3 size={20} />
              Leaderboard & Rankings
            </div>
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`tab-button ${activeTab === 'analytics' ? 'active' : ''}`}
          >
            <div className="flex items-center gap-2">
              <TrendingUp size={20} />
              Analytics
            </div>
          </button>
          <button
            onClick={() => setActiveTab('admin')}
            className={`tab-button ${activeTab === 'admin' ? 'active' : ''}`}
          >
            <div className="flex items-center gap-2">
              <Settings size={20} />
              Admin
            </div>
          </button>
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-b-lg shadow-md p-6">
          {activeTab === 'leaderboard' && <LeaderboardTab />}
          {activeTab === 'analytics' && <AnalyticsTab />}
          {activeTab === 'admin' && <AdminTab />}
        </div>
      </div>
    </div>
  );
}
