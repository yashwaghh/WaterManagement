import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Droplet, Settings, LogOut, ShoppingBag } from 'lucide-react';
import { signOut } from 'firebase/auth';
import { auth } from '../firebase';
import apiService from '../services/api';
import useStore from '../store/useStore';
import LeaderboardTab from './tabs/LeaderboardTab';
import AnalyticsTab from './tabs/AnalyticsTab';
import StoreTab from './tabs/StoreTab';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('leaderboard');
  const [isConnected, setIsConnected] = useState(false);
  const { error, clearError, user, userProfile } = useStore();

  const handleLogout = async () => {
    try {
      await signOut(auth);
    } catch (err) {
      console.error('Error signing out:', err);
    }
  };

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
    <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-teal-50 to-sky-100 relative overflow-hidden">
      {/* Animated SVG water wave background */}
      <div className="absolute bottom-0 left-0 w-full pointer-events-none z-0 opacity-30">
        <svg viewBox="0 0 1440 320" preserveAspectRatio="none" className="w-[200%] h-[200px] animate-wave">
          <path fill="#06b6d4" fillOpacity="0.15" d="M0,160L48,138.7C96,117,192,75,288,74.7C384,75,480,117,576,128C672,139,768,117,864,112C960,107,1056,117,1152,138.7C1248,160,1344,192,1392,208L1440,224L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path>
        </svg>
      </div>
      <div className="absolute bottom-0 left-0 w-full pointer-events-none z-0 opacity-20">
        <svg viewBox="0 0 1440 320" preserveAspectRatio="none" className="w-[200%] h-[160px] animate-wave-slow">
          <path fill="#0891b2" fillOpacity="0.2" d="M0,192L48,186.7C96,181,192,171,288,154.7C384,139,480,117,576,122.7C672,128,768,160,864,170.7C960,181,1056,171,1152,154.7C1248,139,1344,117,1392,106.7L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path>
        </svg>
      </div>
      {/* Decorative background blur elements */}
      <div className="absolute top-0 left-0 w-96 h-96 bg-cyan-400/10 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob"></div>
      <div className="absolute top-0 right-0 w-96 h-96 bg-teal-400/10 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-2000"></div>
      <div className="absolute -bottom-8 left-20 w-96 h-96 bg-blue-400/10 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-4000"></div>

      {/* Header (Glassmorphism) */}
      <header className="bg-white/70 backdrop-blur-lg border-b border-white/50 shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 relative z-10">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-gradient-to-br from-cyan-400 to-blue-600 rounded-xl shadow-md shadow-cyan-500/20 water-ripple">
                <Droplet className="text-white fill-white/20 drop-pulse" size={26} />
              </div>
              <div>
                <h1 className="text-2xl font-black text-slate-800 tracking-tight">Aqua<span className="text-water-gradient">Sync</span></h1>
                <p className="text-xs font-bold text-teal-600 uppercase tracking-widest">Smart Water Analytics</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              {userProfile && (
                <div className="flex items-center gap-3 mr-2 pr-4 border-r border-gray-200 hidden sm:flex">
                  <div className="text-right">
                    <p className="text-sm font-bold text-gray-900">Flat {userProfile.flat_id}</p>
                    <p className="text-xs text-gray-500">{user?.email}</p>
                  </div>
                  <button 
                    onClick={handleLogout}
                    className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-full transition-colors"
                    title="Sign Out"
                  >
                    <LogOut size={20} />
                  </button>
                </div>
              )}
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
      <div className="max-w-7xl mx-auto px-6 py-8 relative z-10">
        {/* Tab Navigation */}
        <div className="flex gap-2 mb-8 border-b border-cyan-100 bg-white/60 backdrop-blur-md rounded-t-2xl px-6 pt-4">
          <button
            onClick={() => setActiveTab('leaderboard')}
            className={`pb-4 px-4 font-bold transition-all border-b-2 ${activeTab === 'leaderboard' ? 'border-cyan-500 text-cyan-700' : 'border-transparent text-slate-500 hover:text-cyan-600 hover:border-cyan-200'}`}
          >
            <div className="flex items-center gap-2">
              <BarChart3 size={20} />
              Rewards Leaderboard
            </div>
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`pb-4 px-4 font-bold transition-all border-b-2 ${activeTab === 'analytics' ? 'border-teal-500 text-teal-700' : 'border-transparent text-slate-500 hover:text-teal-600 hover:border-teal-200'}`}
          >
            <div className="flex items-center gap-2">
              <TrendingUp size={20} />
              My Eco-Analytics
            </div>
          </button>
          <button
            onClick={() => setActiveTab('store')}
            className={`pb-4 px-4 font-bold transition-all border-b-2 ${activeTab === 'store' ? 'border-blue-500 text-blue-700' : 'border-transparent text-slate-500 hover:text-blue-600 hover:border-blue-200'}`}
          >
            <div className="flex items-center gap-2">
              <ShoppingBag size={20} />
              Swag Store
            </div>
          </button>
        </div>

        {/* Tab Content */}
        <div className="bg-white/80 backdrop-blur-xl rounded-b-3xl rounded-tr-3xl shadow-xl shadow-cyan-900/5 border border-white p-6 md:p-8">
          {activeTab === 'leaderboard' && <LeaderboardTab />}
          {activeTab === 'analytics' && <AnalyticsTab />}
          {activeTab === 'store' && <StoreTab />}
        </div>
      </div>
    </div>
  );
}
