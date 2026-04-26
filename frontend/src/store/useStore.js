import create from 'zustand';

export const useStore = create((set) => ({
  // Leaderboard state
  leaderboard: [],
  weeklySummary: [],
  selectedFlat: null,
  currentDay: 1,

  // Analytics state
  analytics: null,
  loading: false,
  error: null,

  // Admin state
  adminState: null,
  simulating: false,

  // Actions
  setLeaderboard: (leaderboard, day) => set({ leaderboard, currentDay: day }),
  setWeeklySummary: (weeklySummary) => set({ weeklySummary }),
  setSelectedFlat: (flatId) => set({ selectedFlat: flatId }),
  setAnalytics: (analytics) => set({ analytics }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  setAdminState: (adminState) => set({ adminState }),
  setSimulating: (simulating) => set({ simulating }),

  clearError: () => set({ error: null }),
}));

export default useStore;
