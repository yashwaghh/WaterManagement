import React, { useEffect, useState } from 'react';
import { LineChart, Line, BarChart, Bar, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, Droplets, Zap, FileText, Download, Calendar, Activity, Award, AlertCircle } from 'lucide-react';
import apiService from '../../services/api';
import useStore from '../../store/useStore';

export default function AnalyticsTab() {
  const { leaderboard, selectedFlat, setSelectedFlat, analytics, setAnalytics, setLoading, loading, setError, userProfile } =
    useStore();
  const [flats, setFlats] = useState([]);
  const [history, setHistory] = useState([]);
  const [completedReports, setCompletedReports] = useState([]);
  
  // Report Generation State
  const [reportType, setReportType] = useState('daily');
  const [singleDay, setSingleDay] = useState(1);
  const [startDay, setStartDay] = useState(1);
  const [endDay, setEndDay] = useState(7);

  // Fetch flats list
  useEffect(() => {
    const fetchFlats = async () => {
      try {
        const response = await apiService.getFlats();
        setFlats(response.data.flats);
        
        // Auto-select the logged-in user's flat
        if (userProfile && userProfile.flat_id) {
          setSelectedFlat(userProfile.flat_id);
        } else if (response.data.flats.length > 0 && !selectedFlat) {
          setSelectedFlat(response.data.flats[0]);
        }
      } catch (err) {
        console.error('Failed to fetch flats:', err);
      }
    };

    fetchFlats();
  }, [userProfile, selectedFlat, setSelectedFlat]);

  // Fetch reports alongside analytics
  useEffect(() => {
    if (!selectedFlat) return;

    const fetchData = async () => {
      setLoading(true);
      try {
        const [, analyticsRes, historyRes, reportsRes] = await Promise.all([
          apiService.getLeaderboard(),       
          apiService.getAnalytics(selectedFlat),
          apiService.getHistory(selectedFlat, 50),
          apiService.getReports(selectedFlat),
        ]);
        setAnalytics(analyticsRes.data);
        setHistory(historyRes.data.history || []);
        setCompletedReports(reportsRes.data.reports || []);
        setError(null);
      } catch (err) {
        setError('Failed to fetch analytics');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [selectedFlat, setAnalytics, setLoading, setError]);

  // Download helper
  const downloadFile = async (url, filename) => {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        alert(errData.error || 'Download failed — no data available for this selection.');
        return;
      }
      const blob = await response.blob();
      const blobUrl = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(blobUrl);
    } catch (err) {
      alert('Download failed. Please check your connection.');
      console.error('Download error:', err);
    }
  };

  const handleGeneratePdf = () => {
    let url, filename;
    if (reportType === 'daily') {
      url = apiService.getDailyPdfUrl(selectedFlat, singleDay);
      filename = `${selectedFlat}_daily_report_day_${singleDay}.pdf`;
    } else if (reportType === 'weekly') {
      url = apiService.getWeeklyPdfUrl(selectedFlat, startDay, endDay);
      filename = `${selectedFlat}_weekly_report_days_${startDay}-${endDay}.pdf`;
    } else if (reportType === 'monthly') {
      url = apiService.getMonthlyPdfUrl(selectedFlat, startDay, endDay);
      filename = `${selectedFlat}_monthly_report_days_${startDay}-${endDay}.pdf`;
    }
    downloadFile(url, filename);
  };

  if (!selectedFlat) {
    return <div className="flex justify-center items-center h-64 text-gray-500 font-medium">No flats available</div>;
  }

  const currentFlat = leaderboard.find((f) => f.flat_id === selectedFlat);

  // Format history data for charts
  const formattedHistory = history.map((h, idx) => ({
    ...h,
    label: h.timestamp ? new Date(h.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : `#${idx}`,
    roundedUsage: Number(h.usage).toFixed(0),
    roundedEfficiency: Number(h.efficiency).toFixed(1)
  }));

  // Calculations for Gamification & Donut Chart
  const threshold = currentFlat ? (currentFlat.target || 2000) : 2000;
  const used = currentFlat ? currentFlat.usage : 0;
  const remaining = Math.max(0, threshold - used);
  const percentageUsedNum = (used / threshold) * 100;
  const percentageUsed = percentageUsedNum.toFixed(1);
  
  const isGood = percentageUsedNum <= 100;
  const isGrace = percentageUsedNum > 100 && percentageUsedNum <= 120;
  const isWarning = percentageUsedNum > 120 && percentageUsedNum <= 150;
  const isPenalty = percentageUsedNum > 150;
  
  // Donut logic: cap rendering at 100% so it doesn't break, but show actual percent in text
  const donutData = [
    { name: 'Used', value: isGood ? used : threshold },
    { name: 'On Track to Save', value: remaining === 0 && used === 0 ? 1 : remaining } 
  ];
  
  let donutColors = ['#14b8a6', '#ccfbf1']; // Teal (Eco-Friendly)
  if (isGrace) donutColors = ['#94a3b8', '#f1f5f9']; // Slate/Freeze
  else if (isWarning) donutColors = ['#f97316', '#ffedd5']; // Orange
  else if (isPenalty) donutColors = ['#ef4444', '#fee2e2']; // Red

  // Dynamic Content for Insights Panel
  let panelColors = "from-teal-50 to-emerald-50 border-teal-100";
  let iconBg = "bg-teal-500";
  let titleText = "🌊 Awesome pacing today!";
  let descText = `You are on track to save ${remaining.toLocaleString()}ml today! Maintain this great pacing to earn maximum Reward Points for the Swag Store.`;
  let tipText = "Turning off the tap while brushing your teeth saves up to 15 liters of water a minute!";
  
  if (isGrace) {
    panelColors = "from-slate-50 to-gray-50 border-slate-200";
    iconBg = "bg-slate-500";
    titleText = "❄️ Streak Frozen!";
    descText = `Hey, you used a bit more than expected today (${percentageUsed}% of target). You didn't earn points, but your streak is FROZEN! Reduce flow tomorrow to keep your streak alive.`;
    tipText = "A single 10-minute shower can use 100 liters of water. Try to keep it to 5 minutes tomorrow!";
  } else if (isWarning) {
    panelColors = "from-orange-50 to-amber-50 border-orange-200";
    iconBg = "bg-orange-500";
    titleText = "⚠️ High Usage Alert!";
    descText = `Warning: You are consuming water at an unsustainable rate (${percentageUsed}% of target). Please stop immediately to avoid severe penalties.`;
    tipText = "Check for running toilets or dripping faucets immediately! A leaky faucet wastes massive amounts of water.";
  } else if (isPenalty) {
    panelColors = "from-red-50 to-rose-50 border-red-300";
    iconBg = "bg-red-600";
    titleText = "🚨 Financial Surcharge Applied!";
    descText = `You have critically exceeded your target (${percentageUsed}%). A 10% surcharge will be applied to your maintenance bill, and you have been moved to the bottom of the Leaderboard.`;
    tipText = "Immediate action is required. If this is a leak, contact building maintenance right away.";
  }

  // Custom Chart Tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 rounded-xl shadow-lg border border-gray-100">
          <p className="text-sm font-bold text-gray-800 mb-2">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm flex items-center gap-2 mb-1" style={{ color: entry.color }}>
              <span className="w-3 h-3 rounded-full" style={{ backgroundColor: entry.color }}></span>
              {entry.name}: <span className="font-semibold">{entry.value}</span>
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-8 animate-fade-in pb-12">
      {/* Personalized Header */}
      <div className="flex items-center justify-between border-b border-gray-100 pb-6">
        <div className="flex items-center gap-4">
          <div className="bg-gradient-to-br from-teal-400 to-emerald-500 p-4 rounded-2xl shadow-sm shadow-teal-500/20 text-white">
            <Activity size={28} />
          </div>
          <div>
            <h2 className="text-2xl font-extrabold text-gray-900 tracking-tight">Analytics: Flat {selectedFlat}</h2>
            <p className="text-gray-500 font-medium">Real-time water consumption insights and history</p>
          </div>
        </div>
        {loading && <span className="text-sm text-teal-600 bg-teal-50 px-3 py-1 rounded-full animate-pulse font-bold border border-teal-100">Live Syncing...</span>}
      </div>

      {/* Summary Stats Cards */}
      {currentFlat && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
            <p className="text-sm text-gray-500 font-semibold uppercase tracking-wider mb-1">Eco Score</p>
            <p className={`text-4xl font-black ${currentFlat.efficiency_score > 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
              {currentFlat.efficiency_score}
            </p>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
            <p className="text-sm text-gray-500 font-semibold uppercase tracking-wider mb-1">Reward Status</p>
            <p className="text-2xl font-bold text-gray-800 mt-2">{currentFlat.status === 'Penalty Zone' ? 'Missed Points' : currentFlat.status}</p>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
            <p className="text-sm text-gray-500 font-semibold uppercase tracking-wider mb-1">Water Usage</p>
            <div className="flex items-end gap-1 mt-1 text-gray-900">
              <span className="text-3xl font-black">{currentFlat.usage.toLocaleString()}</span>
              <span className="text-sm font-medium text-gray-400 mb-1">ml</span>
            </div>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
            <p className="text-sm text-gray-500 font-semibold uppercase tracking-wider mb-1">Earned Points</p>
            <div className="flex items-end gap-1 mt-1 text-amber-500">
              <span className="text-3xl font-black">{currentFlat.daily_points.toLocaleString()}</span>
              <span className="text-sm font-medium mb-1">pts</span>
            </div>
          </div>
        </div>
      )}

      {/* Gamification & Insights Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Water Allowance Donut */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 flex flex-col items-center justify-center relative">
          <h3 className="font-bold text-lg text-gray-900 absolute top-6 left-6">Daily Eco-Target</h3>
          <div className="w-48 h-48 mt-8 relative">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={donutData}
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                  stroke="none"
                  animationDuration={800}
                >
                  {donutData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={donutColors[index % donutColors.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `${Number(value).toFixed(0)} ml`} />
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none mt-2">
              <span className={`text-3xl font-black ${isPenalty ? 'text-red-500' : isWarning ? 'text-orange-500' : isGrace ? 'text-slate-500' : 'text-teal-500'}`}>
                {percentageUsed}%
              </span>
              <span className="text-xs font-semibold text-gray-400 uppercase tracking-widest">Used</span>
            </div>
          </div>
          <div className="w-full flex justify-between text-sm font-medium text-gray-500 mt-2 px-4">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${isPenalty ? 'bg-red-500' : isWarning ? 'bg-orange-500' : isGrace ? 'bg-slate-500' : 'bg-teal-500'}`}></div>
              <span>Used: {used.toLocaleString()}ml</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-slate-200"></div>
              <span>Saved: {remaining.toLocaleString()}ml</span>
            </div>
          </div>
        </div>

        {/* Motivational Insights */}
        <div className={`md:col-span-2 bg-gradient-to-br ${panelColors} rounded-2xl border p-6 flex flex-col justify-center transition-colors duration-500`}>
          <div className="flex items-start gap-4">
            <div className={`p-3 rounded-2xl text-white shadow-sm ${iconBg}`}>
              {isPenalty ? <AlertCircle size={32} /> : isWarning ? <AlertCircle size={32} /> : isGrace ? <AlertCircle size={32} /> : <Award size={32} />}
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-extrabold text-gray-900 mb-2">
                {titleText}
              </h3>
              <p className="text-gray-700 font-medium leading-relaxed mb-4">
                {descText}
              </p>
              
              <div className="bg-white/60 p-4 rounded-xl border border-white/50 shadow-sm mb-3">
                <p className="text-sm font-bold text-gray-800">💡 Tip of the Day:</p>
                <p className="text-sm text-gray-700 mt-1">{tipText}</p>
              </div>
              
              {currentFlat && currentFlat.efficiency_score > 20 && isGood && (
                <div className="inline-flex items-center gap-2 bg-green-100 text-green-800 px-4 py-2 rounded-xl text-sm font-bold shadow-sm">
                  <TrendingUp size={16} /> 🔥 You are highly efficient right now! Keep the streak alive!
                </div>
              )}
              {currentFlat && isPenalty && (
                <div className="inline-flex items-center gap-2 bg-red-100 text-red-800 px-4 py-2 rounded-xl text-sm font-bold shadow-sm">
                  <TrendingUp size={16} className="rotate-180" /> You are actively losing rank!
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Live History Charts */}
      {formattedHistory.length > 1 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Usage + Flow Rate Area Chart */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <div className="mb-6">
              <h3 className="font-bold text-lg text-gray-900 flex items-center gap-2">
                <TrendingUp className="text-blue-500" size={20} />
                Live Flow & Consumption
              </h3>
              <p className="text-sm text-gray-500">Real-time water tracking (Last 50 ticks)</p>
            </div>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={formattedHistory} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorUsage" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorFlow" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                  <XAxis dataKey="label" tick={{ fontSize: 10, fill: '#94a3b8' }} tickLine={false} axisLine={false} />
                  <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} tickLine={false} axisLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend iconType="circle" wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                  <Area type="monotone" dataKey="usage" stroke="#3b82f6" fillOpacity={1} fill="url(#colorUsage)" name="Usage (ml)" strokeWidth={3} />
                  <Area type="monotone" dataKey="flow_rate" stroke="#10b981" fillOpacity={1} fill="url(#colorFlow)" name="Flow Rate (ml/min)" strokeWidth={3} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Efficiency Over Time */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <div className="mb-6">
              <h3 className="font-bold text-lg text-gray-900 flex items-center gap-2">
                <Zap className="text-purple-500" size={20} />
                Efficiency Trend
              </h3>
              <p className="text-sm text-gray-500">How well you are managing your threshold</p>
            </div>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={formattedHistory} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                  <XAxis dataKey="label" tick={{ fontSize: 10, fill: '#94a3b8' }} tickLine={false} axisLine={false} />
                  <YAxis domain={['auto', 100]} tick={{ fontSize: 10, fill: '#94a3b8' }} tickLine={false} axisLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend iconType="circle" wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                  <Line type="monotone" dataKey="roundedEfficiency" stroke="#a855f7" name="Efficiency %" dot={false} strokeWidth={4} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* Unified Report Generator */}
      <div className="bg-gradient-to-r from-gray-900 to-slate-800 rounded-3xl p-8 shadow-xl text-white mt-10">
        <div className="flex items-center gap-3 mb-2">
          <FileText className="text-indigo-400" size={28} />
          <h3 className="font-extrabold text-2xl tracking-tight">On-Demand Report Generator</h3>
        </div>
        <p className="text-slate-400 font-medium mb-8">Generate comprehensive PDF reports for any specific time period.</p>

        <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700/50 backdrop-blur-sm">
          <div className="flex flex-col md:flex-row gap-6 items-end">
            
            <div className="flex-1 min-w-[200px]">
              <label className="block text-sm font-semibold text-slate-300 mb-2">Report Type</label>
              <div className="relative">
                <select 
                  value={reportType} 
                  onChange={(e) => setReportType(e.target.value)}
                  className="w-full appearance-none bg-slate-900 border border-slate-600 text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all font-medium"
                >
                  <option value="daily">Daily Report (Single Day)</option>
                  <option value="weekly">Weekly Report (7-Day Range)</option>
                  <option value="monthly">Monthly Report (30-Day Range)</option>
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-slate-400">
                  <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/></svg>
                </div>
              </div>
            </div>

            {reportType === 'daily' && (
              <div className="flex-1">
                <label className="block text-sm font-semibold text-slate-300 mb-2">Select Day Number</label>
                <input
                  type="number" min="1" value={singleDay}
                  onChange={(e) => setSingleDay(parseInt(e.target.value) || 1)}
                  className="w-full bg-slate-900 border border-slate-600 text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium"
                />
              </div>
            )}

            {(reportType === 'weekly' || reportType === 'monthly') && (
              <>
                <div className="w-1/4">
                  <label className="block text-sm font-semibold text-slate-300 mb-2">Start Day</label>
                  <input
                    type="number" min="1" value={startDay}
                    onChange={(e) => setStartDay(parseInt(e.target.value) || 1)}
                    className="w-full bg-slate-900 border border-slate-600 text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium"
                  />
                </div>
                <div className="w-1/4">
                  <label className="block text-sm font-semibold text-slate-300 mb-2">End Day</label>
                  <input
                    type="number" min="1" value={endDay}
                    onChange={(e) => setEndDay(parseInt(e.target.value) || 7)}
                    className="w-full bg-slate-900 border border-slate-600 text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium"
                  />
                </div>
              </>
            )}

            <button
              onClick={handleGeneratePdf}
              className="bg-indigo-600 hover:bg-indigo-500 text-white px-8 py-3 rounded-xl font-bold transition-colors flex items-center justify-center gap-2 h-[50px] min-w-[200px]"
            >
              <Download size={18} />
              Download PDF
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
