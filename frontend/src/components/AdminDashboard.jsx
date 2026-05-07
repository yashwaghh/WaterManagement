import React, { useState, useEffect } from 'react';
import { Database, Activity, FileText, AlertTriangle, Settings, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/api';
import AdminTab from './tabs/AdminTab';

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const checkConnection = async () => {
      try {
        await apiService.checkHealth();
        setIsConnected(true);
      } catch (err) {
        setIsConnected(false);
      }
    };
    checkConnection();
    const interval = setInterval(checkConnection, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-200">
      {/* Admin Header */}
      <header className="bg-slate-800 border-b border-slate-700 shadow-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button onClick={() => navigate('/')} className="p-2 hover:bg-slate-700 rounded-lg text-slate-400 hover:text-white transition-colors">
                <ArrowLeft size={24} />
              </button>
              <div className="p-2 bg-red-600 rounded-lg shadow-lg shadow-red-900/50">
                <Settings className="text-white" size={24} />
              </div>
              <div>
                <h1 className="text-2xl font-black text-white tracking-tight">System Admin Console</h1>
                <p className="text-sm font-medium text-slate-400">Restricted Access • Management Tools</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider ${
                  isConnected ? 'bg-emerald-900/50 text-emerald-400 border border-emerald-800' : 'bg-red-900/50 text-red-400 border border-red-800'
                }`}
              >
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-red-500'}`} />
                {isConnected ? 'API Online' : 'API Offline'}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="bg-slate-800 rounded-2xl shadow-xl border border-slate-700 p-8">
          <div className="mb-8 pb-6 border-b border-slate-700">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Database className="text-red-500" /> Simulator Controls & Management
            </h2>
            <p className="text-slate-400 mt-2">Force-trigger day resets, wipe databases, and manage sensor endpoints.</p>
          </div>
          
          {/* Reusing the existing AdminTab logic here but styled dark */}
          <div className="admin-console-wrapper">
             <AdminTab />
          </div>
        </div>
      </div>
    </div>
  );
}
