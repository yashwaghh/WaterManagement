import React, { useEffect, useState } from 'react';
import { Settings, RotateCcw, Power } from 'lucide-react';
import apiService from '../../services/api';
import useStore from '../../store/useStore';

export default function AdminTab() {
  const { setAdminState, setError, adminState } = useStore();
  const [isLoading, setIsLoading] = useState(false);
  const [confirmAction, setConfirmAction] = useState(null);

  // Fetch admin state
  const fetchAdminState = async () => {
    try {
      const response = await apiService.getAdminState();
      setAdminState(response.data);
    } catch (err) {
      setError('Failed to fetch admin state');
      console.error(err);
    }
  };

  useEffect(() => {
    fetchAdminState();
    const interval = setInterval(fetchAdminState, 5000);
    return () => clearInterval(interval);
  }, []);

  // Reset day action
  const handleResetDay = async () => {
    setIsLoading(true);
    try {
      await apiService.resetDay();
      setError(null);
      setConfirmAction(null);
      await fetchAdminState();
      alert('✅ Day reset successful!');
    } catch (err) {
      setError('Failed to reset day');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Reset week action
  const handleResetWeek = async () => {
    setIsLoading(true);
    try {
      await apiService.resetWeek();
      setError(null);
      setConfirmAction(null);
      await fetchAdminState();
      alert('✅ Week reset successful!');
    } catch (err) {
      setError('Failed to reset week');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Toggle simulation
  const handleToggleSimulation = async () => {
    setIsLoading(true);
    try {
      const response = await apiService.toggleSimulation();
      setError(null);
      setConfirmAction(null);
      alert(`✅ ${response.data.message}`);
    } catch (err) {
      setError('Failed to toggle simulation');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-yellow-800 text-sm font-medium">
          ⚠️ Admin controls affect the entire system. Use with caution.
        </p>
      </div>

      {/* Current State */}
      <div className="card">
        <div className="card-header">
          <h3 className="font-bold text-lg text-gray-900 flex items-center gap-2">
            <Settings size={20} />
            System State
          </h3>
        </div>
        {adminState && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <p className="text-sm text-gray-600">Current Day</p>
              <p className="text-3xl font-bold text-primary-600">{adminState.current_day}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <p className="text-sm text-gray-600">Flats in System</p>
              <p className="text-3xl font-bold text-primary-600">{adminState.flats_count}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <p className="text-sm text-gray-600">Total Weekly Points</p>
              <p className="text-2xl font-bold text-primary-600">
                {Object.values(adminState.weekly_points || {}).reduce((a, b) => a + b, 0).toLocaleString()}
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <p className="text-sm text-gray-600">Cycle Start</p>
              <p className="text-xs font-mono text-gray-700 truncate">
                {new Date(adminState.cycle_start_time).toLocaleTimeString()}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Reset Day Button */}
        <div className="card">
          <div className="card-header">
            <h4 className="font-bold text-gray-900 flex items-center gap-2">
              <RotateCcw size={18} />
              Reset Day
            </h4>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            Move to the next day, clear current readings, and finalize leaderboard.
          </p>
          {confirmAction === 'reset-day' ? (
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-900">Are you sure?</p>
              <div className="flex gap-2">
                <button
                  onClick={handleResetDay}
                  disabled={isLoading}
                  className="flex-1 bg-red-600 text-white px-3 py-2 rounded font-medium hover:bg-red-700 disabled:opacity-50"
                >
                  {isLoading ? 'Resetting...' : 'Confirm'}
                </button>
                <button
                  onClick={() => setConfirmAction(null)}
                  className="flex-1 bg-gray-200 text-gray-800 px-3 py-2 rounded font-medium hover:bg-gray-300"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <button
              onClick={() => setConfirmAction('reset-day')}
              className="w-full btn-primary"
            >
              Reset Day
            </button>
          )}
        </div>

        {/* Reset Week Button */}
        <div className="card">
          <div className="card-header">
            <h4 className="font-bold text-gray-900 flex items-center gap-2">
              <RotateCcw size={18} />
              Reset Week
            </h4>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            Clear all weekly points, reset day counter to 1, and start fresh.
          </p>
          {confirmAction === 'reset-week' ? (
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-900">Are you sure? This will clear all data.</p>
              <div className="flex gap-2">
                <button
                  onClick={handleResetWeek}
                  disabled={isLoading}
                  className="flex-1 bg-red-600 text-white px-3 py-2 rounded font-medium hover:bg-red-700 disabled:opacity-50"
                >
                  {isLoading ? 'Resetting...' : 'Confirm'}
                </button>
                <button
                  onClick={() => setConfirmAction(null)}
                  className="flex-1 bg-gray-200 text-gray-800 px-3 py-2 rounded font-medium hover:bg-gray-300"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <button
              onClick={() => setConfirmAction('reset-week')}
              className="w-full btn-primary"
            >
              Reset Week
            </button>
          )}
        </div>

        {/* Toggle Simulation Button */}
        <div className="card">
          <div className="card-header">
            <h4 className="font-bold text-gray-900 flex items-center gap-2">
              <Power size={18} />
              Toggle Simulation
            </h4>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            Switch between simulation and Firebase mode. Restart app to apply.
          </p>
          {confirmAction === 'toggle-sim' ? (
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-900">Switch modes?</p>
              <div className="flex gap-2">
                <button
                  onClick={handleToggleSimulation}
                  disabled={isLoading}
                  className="flex-1 bg-purple-600 text-white px-3 py-2 rounded font-medium hover:bg-purple-700 disabled:opacity-50"
                >
                  {isLoading ? 'Switching...' : 'Confirm'}
                </button>
                <button
                  onClick={() => setConfirmAction(null)}
                  className="flex-1 bg-gray-200 text-gray-800 px-3 py-2 rounded font-medium hover:bg-gray-300"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <button
              onClick={() => setConfirmAction('toggle-sim')}
              className="w-full btn-secondary"
            >
              Toggle Mode
            </button>
          )}
        </div>
      </div>

      {/* Weekly Points Breakdown */}
      {adminState && Object.keys(adminState.weekly_points || {}).length > 0 && (
        <div className="card">
          <div className="card-header">
            <h4 className="font-bold text-gray-900">Weekly Points Breakdown</h4>
          </div>
          <div className="space-y-2">
            {Object.entries(adminState.weekly_points).map(([flatId, points]) => (
              <div
                key={flatId}
                className="flex justify-between items-center p-3 bg-gray-50 rounded-lg"
              >
                <span className="font-medium text-gray-900">{flatId}</span>
                <span className="text-primary-600 font-bold">
                  {points.toLocaleString()} points
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Documentation */}
      <div className="card bg-blue-50 border border-blue-200">
        <div className="card-header">
          <h4 className="font-bold text-gray-900">📖 Admin Guide</h4>
        </div>
        <ul className="space-y-2 text-sm text-gray-700">
          <li>
            <strong>Reset Day:</strong> Moves to the next simulated day. Current rankings are finalized and
            daily points are accumulated to weekly totals.
          </li>
          <li>
            <strong>Reset Week:</strong> Clears all accumulated points and resets back to Day 1. Use at the
            end of a weekly cycle.
          </li>
          <li>
            <strong>Toggle Simulation:</strong> Switches between simulated data (local generation) and
            Firebase mode (real data). Requires app restart.
          </li>
          <li>
            <strong>System State:</strong> Shows the current day, number of flats, and cycle timing
            information.
          </li>
        </ul>
      </div>
    </div>
  );
}
