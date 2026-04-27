import React, { useEffect, useState } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, Droplets, Zap } from 'lucide-react';
import apiService from '../../services/api';
import useStore from '../../store/useStore';

export default function AnalyticsTab() {
  const { leaderboard, selectedFlat, setSelectedFlat, analytics, setAnalytics, setLoading, loading, setError } =
    useStore();
  const [flats, setFlats] = useState([]);
  const [history, setHistory] = useState([]);

  // Fetch flats list
  useEffect(() => {
    const fetchFlats = async () => {
      try {
        const response = await apiService.getFlats();
        setFlats(response.data.flats);
        if (response.data.flats.length > 0 && !selectedFlat) {
          setSelectedFlat(response.data.flats[0]);
        }
      } catch (err) {
        console.error('Failed to fetch flats:', err);
      }
    };

    fetchFlats();
  }, []);

  // Fetch analytics + history for selected flat
  useEffect(() => {
    if (!selectedFlat) return;

    const fetchData = async () => {
      setLoading(true);
      try {
        const [analyticsRes, historyRes] = await Promise.all([
          apiService.getAnalytics(selectedFlat),
          apiService.getHistory(selectedFlat, 50),
        ]);
        setAnalytics(analyticsRes.data);
        setHistory(historyRes.data.history || []);
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

  if (!selectedFlat) {
    return <div className="text-gray-500 py-8">No flats available</div>;
  }

  const currentFlat = leaderboard.find((f) => f.flat_id === selectedFlat);

  return (
    <div className="space-y-6">
      {/* Flat Selector */}
      <div className="flex gap-2 flex-wrap">
        {flats.map((flat) => (
          <button
            key={flat}
            onClick={() => setSelectedFlat(flat)}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              selectedFlat === flat
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {flat}
          </button>
        ))}
      </div>

      {/* Summary Stats */}
      {currentFlat && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="card">
            <p className="text-sm text-gray-600">Efficiency Score</p>
            <p className={`text-3xl font-bold ${currentFlat.efficiency_score > 0 ? 'text-green-600' : 'text-red-600'}`}>
              {currentFlat.efficiency_score}
            </p>
          </div>
          <div className="card">
            <p className="text-sm text-gray-600">Status</p>
            <p className="text-lg font-bold text-gray-900">{currentFlat.status}</p>
          </div>
          <div className="card">
            <p className="text-sm text-gray-600">Usage</p>
            <div className="flex items-center gap-1 text-gray-900">
              <Droplets size={18} className="text-blue-600" />
              <span className="text-xl font-bold">{currentFlat.usage.toLocaleString()}</span>
              <span className="text-xs text-gray-500">ml</span>
            </div>
          </div>
          <div className="card">
            <p className="text-sm text-gray-600">Daily Points</p>
            <div className="flex items-center gap-1 text-gray-900">
              <Zap size={18} className="text-amber-600" />
              <span className="text-xl font-bold">{currentFlat.daily_points.toLocaleString()}</span>
            </div>
          </div>
        </div>
      )}

      {/* Efficiency Trend Chart */}
      {analytics && analytics.efficiency_trend && analytics.efficiency_trend.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h3 className="font-bold text-lg text-gray-900 flex items-center gap-2">
              <TrendingUp size={20} />
              Efficiency Trend
            </h3>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={analytics.efficiency_trend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="timestamp"
                tick={{ fontSize: 12 }}
                interval={Math.floor(analytics.efficiency_trend.length / 6)}
              />
              <YAxis />
              <Tooltip
                contentStyle={{ backgroundColor: '#f3f4f6', border: '1px solid #e5e7eb' }}
                formatter={(value) => value.toFixed(2)}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="efficiency"
                stroke="#0ea5e9"
                name="Efficiency Score"
                dot={false}
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Usage Over Time */}
      {analytics && analytics.efficiency_trend && analytics.efficiency_trend.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h3 className="font-bold text-lg text-gray-900 flex items-center gap-2">
              <Droplets size={20} />
              Usage Over Time
            </h3>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={analytics.efficiency_trend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="timestamp"
                tick={{ fontSize: 12 }}
                interval={Math.floor(analytics.efficiency_trend.length / 6)}
              />
              <YAxis />
              <Tooltip contentStyle={{ backgroundColor: '#f3f4f6', border: '1px solid #e5e7eb' }} />
              <Legend />
              <Bar dataKey="usage" fill="#10b981" name="Usage (ml)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Detailed Stats */}
      {analytics && (
        <div className="card">
          <div className="card-header">
            <h3 className="font-bold text-lg text-gray-900">Detailed Statistics</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <p className="text-sm text-gray-600 font-medium">Total Usage</p>
              <p className="text-2xl font-bold text-blue-600">
                {analytics.total_usage ? analytics.total_usage.toLocaleString() : 'N/A'}
              </p>
              <p className="text-xs text-gray-500 mt-1">ml</p>
            </div>
            <div className="bg-green-50 rounded-lg p-4 border border-green-200">
              <p className="text-sm text-gray-600 font-medium">Average Usage</p>
              <p className="text-2xl font-bold text-green-600">
                {analytics.average_usage ? analytics.average_usage.toLocaleString() : 'N/A'}
              </p>
              <p className="text-xs text-gray-500 mt-1">ml</p>
            </div>
            <div className="bg-red-50 rounded-lg p-4 border border-red-200">
              <p className="text-sm text-gray-600 font-medium">Peak Usage</p>
              <p className="text-2xl font-bold text-red-600">
                {analytics.peak_usage ? analytics.peak_usage.toLocaleString() : 'N/A'}
              </p>
              <p className="text-xs text-gray-500 mt-1">ml</p>
            </div>
          </div>
        </div>
      )}

      {loading && <div className="text-center text-gray-500 py-8">Loading analytics...</div>}
    </div>
  );
}
