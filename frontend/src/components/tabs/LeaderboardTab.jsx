import React, { useEffect, useState } from 'react';
import { Trophy, TrendingUp, Zap, Droplets, AlertTriangle, Flame, Medal, Target, Users, AlertCircle, ArrowDown, ArrowUp } from 'lucide-react';
import apiService from '../../services/api';
import useStore from '../../store/useStore';

export default function LeaderboardTab() {
  const { leaderboard, currentDay, setLeaderboard, setLoading, loading, setError, userProfile } = useStore();
  const [weeklySummary, setWeeklySummary] = useState([]);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [alertedFlats, setAlertedFlats] = useState(new Set());
  const [userReports, setUserReports] = useState([]);

  // Data Fetching
  const fetchLeaderboard = async () => {
    setLoading(true);
    try {
      const response = await apiService.getLeaderboard();
      setLeaderboard(response.data.leaderboard, response.data.day);
      setError(null);
    } catch (err) {
      setError('Failed to fetch leaderboard');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchWeeklySummary = async () => {
    try {
      const response = await apiService.getWeeklySummary();
      setWeeklySummary(response.data.week_summary);
    } catch (err) {
      console.error('Failed to fetch weekly summary:', err);
    }
  };

  const fetchAlerts = async () => {
    try {
      const response = await apiService.getAlerts();
      const ids = new Set(response.data.alerts.map((a) => a.flat_id));
      setAlertedFlats(ids);
    } catch (err) {
      console.error('Failed to fetch alerts:', err);
    }
  };

  const fetchUserReports = async () => {
    if (!userProfile?.flat_id) return;
    try {
      const res = await apiService.getReports(userProfile.flat_id);
      setUserReports(res.data.reports || []);
    } catch (e) {
      console.error('Failed to fetch user reports:', e);
    }
  };

  useEffect(() => {
    fetchLeaderboard();
    fetchWeeklySummary();
    fetchAlerts();
    fetchUserReports();

    if (autoRefresh) {
      const interval = setInterval(() => {
        fetchLeaderboard();
        fetchWeeklySummary();
        fetchAlerts();
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, userProfile]);

  // Gamification Calculations
  const userFlatId = userProfile?.flat_id;
  const myFlatData = leaderboard.find((f) => f.flat_id === userFlatId);
  const threshold = myFlatData ? myFlatData.target : 2000;

  // 1. Streak Calculation
  let streak = 0;
  let isFrozen = false;
  let isSurcharged = false;

  if (myFlatData) {
    const usageP = (myFlatData.usage / threshold) * 100;
    if (usageP <= 100) streak = 1;
    else if (usageP <= 120) { streak = 1; isFrozen = true; }
    else streak = 0; // broke the streak
    
    if (usageP > 150) isSurcharged = true;
  }
  
  if (streak > 0 && userReports.length > 0) {
    const sorted = [...userReports].sort((a, b) => b.day - a.day);
    for (let r of sorted) {
      const p = (r.total_usage_ml / threshold) * 100;
      if (p <= 100) streak++;
      else if (p <= 120) streak++; // Grace day maintains streak
      else break;
    }
  }

  // 2. Social Proof / Peer Comparison
  let socialProofMsg = "Gathering data to compare with neighbors...";
  let socialProofIsGood = true;
  let percentDiff = 0;

  if (myFlatData && leaderboard.length > 1) {
    const totalUsage = leaderboard.reduce((sum, f) => sum + f.usage, 0);
    const avgUsage = (totalUsage - myFlatData.usage) / (leaderboard.length - 1);
    
    if (avgUsage > 0) {
      if (myFlatData.usage < avgUsage) {
        percentDiff = (((avgUsage - myFlatData.usage) / avgUsage) * 100).toFixed(0);
        socialProofMsg = `You are using ${percentDiff}% LESS water than your neighbors today! Keep it up to secure your rewards.`;
        socialProofIsGood = true;
      } else {
        percentDiff = (((myFlatData.usage - avgUsage) / avgUsage) * 100).toFixed(0);
        socialProofMsg = `You are using ${percentDiff}% MORE water than your neighbors. Reduce flow to secure your daily Reward Points!`;
        socialProofIsGood = false;
      }
    }
  }

  // 3. Tier System Calculation
  const getTier = (rank, usage, target) => {
    const p = (usage / (target || 2000)) * 100;
    if (p > 150) return { name: 'Surcharged', badge: 'bg-red-100 text-red-900 border-red-300 font-black', icon: '🚨' };
    if (p > 120) return { name: 'Warning', badge: 'bg-orange-100 text-orange-800 border-orange-200', icon: '⚠️' };
    if (p > 100) return { name: 'Grace Zone', badge: 'bg-slate-100 text-slate-600 border-slate-200', icon: '❄️' };
    
    if (rank === 1) return { name: 'Diamond Tier', badge: 'bg-cyan-100 text-cyan-800 border-cyan-200', icon: '💎' };
    if (rank <= 3) return { name: 'Gold Tier', badge: 'bg-amber-100 text-amber-800 border-amber-200', icon: '🥇' };
    if (rank <= 6) return { name: 'Silver Tier', badge: 'bg-slate-100 text-slate-800 border-slate-300', icon: '🥈' };
    return { name: 'Bronze Tier', badge: 'bg-orange-50 text-orange-800 border-orange-200', icon: '🥉' };
  };

  const myTier = myFlatData ? getTier(myFlatData.rank, myFlatData.usage, myFlatData.target) : null;

  return (
    <div className="space-y-8 animate-fade-in pb-12">
      {/* Leak alert banner */}
      {alertedFlats.size > 0 && (
        <div className="flex items-center gap-3 rounded-xl bg-red-50 border border-red-300 px-6 py-4 shadow-sm text-red-900 animate-pulse">
          <AlertTriangle size={24} className="shrink-0 text-red-600" />
          <span className="font-bold text-lg">CRITICAL: Leak Detected</span>
          <span className="text-md font-medium">
            Flats: {[...alertedFlats].join(', ')} — Continuous maximum flow detected. Immediate action required.
          </span>
        </div>
      )}

      {/* Header */}
      <div className="flex justify-between items-center border-b pb-4">
        <div className="flex items-center gap-4">
          <div className="bg-gradient-to-br from-indigo-500 to-purple-600 p-4 rounded-2xl shadow-sm text-white">
            <Trophy size={28} />
          </div>
          <div>
            <h2 className="text-2xl font-extrabold text-gray-900 tracking-tight">Rewards Leaderboard</h2>
            <p className="text-gray-500 font-medium">Day {currentDay} Live Rankings & Tiers</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 cursor-pointer bg-white px-4 py-2 rounded-xl shadow-sm border border-gray-100">
            <div className={`w-10 h-6 rounded-full p-1 transition-colors ${autoRefresh ? 'bg-green-500' : 'bg-gray-300'}`}>
              <div className={`w-4 h-4 bg-white rounded-full shadow-md transform transition-transform ${autoRefresh ? 'translate-x-4' : 'translate-x-0'}`}></div>
            </div>
            <span className="text-sm font-bold text-gray-700">Live Sync</span>
          </label>
        </div>
      </div>

      {/* HERO BANNER: Personalized Gamification Dashboard */}
      {myFlatData && (
        <div className="bg-gradient-to-r from-slate-900 via-sky-900 to-cyan-900 rounded-3xl p-8 shadow-2xl text-white relative overflow-hidden">
          {/* Water shimmer overlay */}
          <div className="absolute inset-0 water-shimmer rounded-3xl"></div>
          {/* Wave decoration at bottom */}
          <div className="absolute bottom-0 left-0 w-full opacity-10 pointer-events-none">
            <svg viewBox="0 0 1440 120" preserveAspectRatio="none" className="w-full h-[40px]">
              <path fill="#06b6d4" d="M0,64L60,58.7C120,53,240,43,360,48C480,53,600,75,720,80C840,85,960,75,1080,64C1200,53,1320,43,1380,37.3L1440,32L1440,120L0,120Z"/>
            </svg>
          </div>
          {/* Background decoration */}
          <div className="absolute top-0 right-0 -mr-16 -mt-16 opacity-10">
            <Target size={250} />
          </div>
          
          <div className="relative z-10 flex flex-col md:flex-row gap-8 items-center">
            {/* Tier & Profile */}
            <div className="flex-1 text-center md:text-left">
              <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-1">Your Status</h3>
              <div className="flex items-center justify-center md:justify-start gap-3 mb-4">
                <span className="text-4xl">{myTier.icon}</span>
                <h2 className="text-4xl font-black text-white">{myTier.name}</h2>
              </div>
              <p className="text-slate-300 font-medium">
                Rank #{myFlatData.rank} out of {leaderboard.length} flats
              </p>
            </div>

            {/* Streak Counter */}
            <div className={`backdrop-blur-md rounded-2xl p-6 border flex flex-col items-center justify-center min-w-[200px] ${
              isSurcharged ? 'bg-red-900/50 border-red-500/50' : isFrozen ? 'bg-sky-800/50 border-cyan-500/50' : 'bg-sky-900/40 border-cyan-500/30'
            }`}>
              <div className="flex items-center gap-2 mb-2">
                <Flame size={28} className={isSurcharged ? "text-red-500" : isFrozen ? "text-cyan-300" : (streak > 0 ? "text-amber-400 drop-shadow-md" : "text-sky-700")} />
                <span className="font-bold text-lg text-cyan-100">Daily Streak</span>
              </div>
              <div className="text-5xl font-black text-white mb-1 drop-shadow-sm">
                {streak} <span className="text-xl text-cyan-300 font-bold">Days</span>
              </div>
              <p className="text-xs text-cyan-200/70 font-medium text-center">
                {isSurcharged ? "Surcharge applied!" : isFrozen ? "Streak Frozen!" : streak === 0 ? "Target missed!" : "Stay under target!"}
              </p>
            </div>

            {/* Social Proof */}
            <div className={`flex-1 rounded-2xl p-6 border backdrop-blur-md ${socialProofIsGood ? 'bg-emerald-500/10 border-emerald-400/30' : 'bg-red-500/10 border-red-500/30'}`}>
              <div className="flex items-center gap-2 mb-3">
                <Users size={20} className={socialProofIsGood ? "text-emerald-400" : "text-red-400"} />
                <span className="font-bold text-sm text-cyan-100 uppercase tracking-wider">Peer Comparison</span>
              </div>
              <div className="flex items-start gap-3">
                {socialProofIsGood ? (
                  <ArrowDown size={32} className="text-emerald-400 shrink-0 filter drop-shadow-md" />
                ) : (
                  <ArrowUp size={32} className="text-red-400 shrink-0 filter drop-shadow-md" />
                )}
                <div>
                  <h4 className={`text-2xl font-black mb-1 drop-shadow-sm ${socialProofIsGood ? 'text-emerald-400' : 'text-red-400'}`}>
                    {percentDiff}% {socialProofIsGood ? 'Less' : 'More'}
                  </h4>
                  <p className="text-sm text-cyan-50 font-medium leading-relaxed">
                    {socialProofMsg}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Global Rankings Table */}
      <div className="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-6 border-b border-gray-100 bg-gray-50 flex items-center gap-2">
          <Medal className="text-indigo-500" size={24} />
          <h3 className="font-extrabold text-xl text-gray-900">Current Standings</h3>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-white border-b border-gray-100">
              <tr>
                <th className="text-left py-4 px-6 font-bold text-gray-400 uppercase tracking-wider text-xs">Rank</th>
                <th className="text-left py-4 px-6 font-bold text-gray-400 uppercase tracking-wider text-xs">Flat & Tier</th>
                <th className="text-center py-4 px-6 font-bold text-gray-400 uppercase tracking-wider text-xs">Eco Score</th>
                <th className="text-center py-4 px-6 font-bold text-gray-400 uppercase tracking-wider text-xs">Usage</th>
                <th className="text-center py-4 px-6 font-bold text-gray-400 uppercase tracking-wider text-xs">Reward Points</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {leaderboard.map((entry) => {
                const tier = getTier(entry.rank, entry.usage, entry.target);
                const isMe = entry.flat_id === userFlatId;
                
                return (
                  <tr key={entry.flat_id} className={`transition-colors ${isMe ? 'bg-indigo-50/50' : tier.name.includes('Surcharge') ? 'bg-red-50' : 'hover:bg-gray-50'}`}>
                    {/* Rank */}
                    <td className="py-5 px-6">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center font-black text-lg ${
                        entry.rank === 1 ? 'bg-gradient-to-br from-yellow-300 to-amber-500 text-white shadow-md' :
                        entry.rank === 2 ? 'bg-gradient-to-br from-gray-300 to-gray-400 text-white shadow-md' :
                        entry.rank === 3 ? 'bg-gradient-to-br from-orange-400 to-amber-700 text-white shadow-md' :
                        'bg-gray-100 text-gray-500'
                      }`}>
                        {entry.rank}
                      </div>
                    </td>
                    
                    {/* Flat & Tier */}
                    <td className="py-5 px-6">
                      <div className="flex flex-col">
                        <div className="flex items-center gap-2">
                          <span className={`font-extrabold text-lg ${isMe ? 'text-indigo-700' : 'text-gray-900'}`}>
                            {entry.flat_id} {isMe && '(You)'}
                          </span>
                          {alertedFlats.has(entry.flat_id) && (
                            <span className="inline-flex items-center gap-1 rounded-full bg-red-100 px-2 py-0.5 text-xs font-bold text-red-700 animate-pulse">
                              <AlertTriangle size={12} /> Leak
                            </span>
                          )}
                        </div>
                        <div className="mt-1">
                          <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-bold border ${tier.badge}`}>
                            {tier.icon} {tier.name}
                          </span>
                        </div>
                      </div>
                    </td>

                    {/* Efficiency Score */}
                    <td className="py-5 px-6 text-center">
                      <div className={`inline-flex items-center justify-center gap-1.5 px-3 py-1 rounded-xl font-bold ${
                        entry.efficiency_score < 0 ? 'bg-red-100 text-red-700' : 
                        entry.efficiency_score > 20 ? 'bg-green-100 text-green-700' : 'bg-blue-50 text-blue-700'
                      }`}>
                        <TrendingUp size={16} className={entry.efficiency_score < 0 ? 'rotate-180' : ''} />
                        {entry.efficiency_score}
                      </div>
                    </td>

                    {/* Usage */}
                    <td className="py-5 px-6 text-center">
                      <div className="flex flex-col items-center">
                        <span className="font-bold text-gray-800 flex items-center gap-1">
                          <Droplets size={16} className="text-blue-500" />
                          {entry.usage.toLocaleString()} ml
                        </span>
                        <span className="text-xs font-medium text-gray-400 mt-0.5">
                          Peak: {entry.peak_flow.toLocaleString()} ml/min
                        </span>
                      </div>
                    </td>

                    {/* Points */}
                    <td className="py-5 px-6 text-center">
                      <div className={`font-black text-xl flex items-center justify-center gap-1 ${
                        entry.efficiency_score < 0 ? 'text-red-500' : 'text-amber-500'
                      }`}>
                        <Zap size={20} />
                        {entry.daily_points.toLocaleString()}
                      </div>
                      {entry.efficiency_score < 0 && (
                        <p className="text-[10px] font-bold text-red-500 uppercase mt-1">0 Points</p>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
