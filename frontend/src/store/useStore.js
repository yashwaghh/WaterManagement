import { create } from 'zustand';

export const useStore = create((set) => ({
  // --- EXISTING STATE ---
  leaderboard: [],
  weeklySummary: [],
  selectedFlat: null,
  currentDay: 1,
  analytics: null,
  loading: false,
  error: null,
  adminState: null,
  simulating: false,

  // --- NEW AUTH STATE ---
  user: null,          
  userProfile: null,   
  authLoading: true,   

  // --- EXISTING ACTIONS ---
  setLeaderboard: (leaderboard, day) => set({ leaderboard, currentDay: day }),
  setWeeklySummary: (weeklySummary) => set({ weeklySummary }),
  setSelectedFlat: (flatId) => set({ selectedFlat: flatId }),
  setAnalytics: (analytics) => set({ analytics }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  setAdminState: (adminState) => set({ adminState }),
  setSimulating: (simulating) => set({ simulating }),
  clearError: () => set({ error: null }),

  // --- NEW AUTH ACTIONS ---
  setUser: (user) => set({ user }),
  setUserProfile: (profile) => set({ userProfile: profile }),
  setAuthLoading: (status) => set({ authLoading: status }),
}));

export default useStore;
