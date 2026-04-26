import React, { useEffect, useState } from 'react';
import { Trophy, TrendingUp, Zap, Droplets } from 'lucide-react';
import apiService from '../../services/api';
import useStore from '../../store/useStore';

export default function LeaderboardTab() {
  const { leaderboard, currentDay, setLeaderboard, setLoading, loading, setError } =
    useStore();
  const [weeklySummary, setWeeklySummary] = useState([]);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Fetch leaderboard
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

  // Fetch weekly summary
  const fetchWeeklySummary = async () => {
    try {
      const response = await apiService.getWeeklySummary();
      setWeeklySummary(response.data.week_summary);
    } catch (err) {
      console.error('Failed to fetch weekly summary:', err);
    }
  };

  // Initial fetch and setup auto-refresh
  useEffect(() => {
    fetchLeaderboard();
    fetchWeeklySummary();

    if (autoRefresh) {
      const interval = setInterval(() => {
        fetchLeaderboard();
        fetchWeeklySummary();
      }, 5000); // Refresh every 5 seconds

      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const getStatusBadge = (status) => {
    const badgeClass = {
      Efficient: 'badge-efficient',
      Normal: 'badge-normal',
      High: 'badge-high',
      Penalty: 'bg-red-100 text-red-700',
    };
    return badgeClass[status] || 'bg-gray-100 text-gray-700';
  };

  return (
    <div className="space-y-6">
      {/* Header with controls */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Daily Leaderboard</h2>
          <p className="text-gray-600">Day {currentDay} Rankings</p>
        </div>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="w-4 h-4 rounded"
            />
            <span className="text-sm font-medium text-gray-700">Auto-refresh</span>
          </label>
          <button
            onClick={() => {
              fetchLeaderboard();
              fetchWeeklySummary();
            }}
            className="btn-secondary"
            disabled={loading}
          >
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Daily Leaderboard Table */}
      <div className="card">
        <div className="card-header">
          <h3 className="font-bold text-lg text-gray-900 flex items-center gap-2">
            <Trophy size={20} className="text-amber-500" />
            Current Rankings
          </h3>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Rank</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Flat ID</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">Efficiency Score</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Status</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">Usage (ml)</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">Peak Flow</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">Daily Points</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {leaderboard.map((entry) => (
                <tr
                  key={entry.flat_id}
                  className="hover:bg-gray-50 transition-colors"
                >
                  <td className="py-4 px-4">
                    <div className="flex items-center gap-2">
                      {entry.rank <= 3 ? (
                        <div
                          className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-white ${
                            entry.rank === 1
                              ? 'bg-amber-500'
                              : entry.rank === 2
                              ? 'bg-gray-400'
                              : 'bg-amber-700'
                          }`}
                        >
                          {entry.rank}
                        </div>
                      ) : (
                        <div className="w-8 h-8 flex items-center justify-center font-bold text-gray-600">
                          {entry.rank}
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="py-4 px-4 font-medium text-gray-900">{entry.flat_id}</td>
                  <td className="py-4 px-4 text-center">
                    <div className="flex items-center justify-center gap-2">
                      <TrendingUp
                        size={16}
                        className={
                          entry.efficiency_score > 0
                            ? 'text-green-600'
                            : 'text-red-600'
                        }
                      />
                      <span
                        className={`font-bold ${
                          entry.efficiency_score > 0
                            ? 'text-green-600'
                            : 'text-red-600'
                        }`}
                      >
                        {entry.efficiency_score}
                      </span>
                    </div>
                  </td>
                  <td className="py-4 px-4">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusBadge(entry.status)}`}>
                      {entry.status}
                    </span>
                  </td>
                  <td className="py-4 px-4 text-center">
                    <div className="flex items-center justify-center gap-1 text-gray-700">
                      <Droplets size={16} />
                      {entry.usage.toLocaleString()}
                    </div>
                  </td>
                  <td className="py-4 px-4 text-center text-gray-700">
                    {entry.peak_flow.toLocaleString()} ml/s
                  </td>
                  <td className="py-4 px-4 text-center">
                    <div className="flex items-center justify-center gap-1 font-semibold text-primary-600">
                      <Zap size={16} />
                      {entry.daily_points.toLocaleString()}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {leaderboard.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <p>No data available yet. Data will appear as readings are generated.</p>
          </div>
        )}
      </div>

      {/* Weekly Summary */}
      <div className="card">
        <div className="card-header">
          <h3 className="font-bold text-lg text-gray-900 flex items-center gap-2">
            <Trophy size={20} className="text-purple-500" />
            Weekly Cumulative Points
          </h3>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {weeklySummary.map((entry, idx) => (
            <div
              key={entry.flat_id}
              className={`stat-box border-l-4 ${
                idx < 3 ? 'border-l-amber-500' : 'border-l-primary-600'
              }`}
            >
              <p className="text-sm text-gray-600 font-medium">{entry.flat_id}</p>
              <p className="text-2xl font-bold text-primary-600">
                {entry.weekly_points.toLocaleString()}
              </p>
              <p className="text-xs text-gray-500">points</p>
            </div>
          ))}
        </div>

        {weeklySummary.length === 0 && (
          <p className="text-center text-gray-500 py-4">Weekly data will appear after the first day completes.</p>
        )}
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card">
          <p className="text-sm text-gray-600">Total Flats</p>
          <p className="text-3xl font-bold text-primary-600">{leaderboard.length}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600">Current Day</p>
          <p className="text-3xl font-bold text-primary-600">{currentDay}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600">Top Performer</p>
          <p className="text-lg font-bold text-gray-900">
            {leaderboard[0]?.flat_id || 'N/A'}
          </p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600">Avg Efficiency</p>
          <p className="text-lg font-bold text-gray-900">
            {leaderboard.length > 0
              ? (
                  leaderboard.reduce((sum, e) => sum + e.efficiency_score, 0) /
                  leaderboard.length
                ).toFixed(1)
              : '0'}
          </p>
        </div>
      </div>
    </div>
  );
}
