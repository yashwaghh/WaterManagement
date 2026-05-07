import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { onAuthStateChanged } from 'firebase/auth';
import { ref, get } from 'firebase/database';
import { auth, db } from './firebase';
import { useStore } from './store/useStore';

// Components
import LandingPage from './components/LandingPage';
import Dashboard from './components/Dashboard';
import Login from './components/auth/Login';
import OnboardingWizard from './components/auth/OnboardingWizard';
import AdminDashboard from './components/AdminDashboard';
import './index.css';

function App() {
  const { user, userProfile, authLoading, setUser, setUserProfile, setAuthLoading } = useStore();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (currentUser) => {
      setUser(currentUser);
      
      if (currentUser) {
        try {
          const dbRef = ref(db, `users/${currentUser.uid}`);
          const snapshot = await get(dbRef);
          
          if (snapshot.exists()) {
            setUserProfile(snapshot.val());
          } else {
            setUserProfile(null); 
          }
        } catch (error) {
          console.error("Error fetching user profile:", error);
        }
      } else {
        setUserProfile(null);
      }
      setAuthLoading(false);
    });

    return () => unsubscribe();
  }, [setUser, setUserProfile, setAuthLoading]);

  if (authLoading) {
    return <div className="flex h-screen items-center justify-center bg-gray-50"><p>Loading App...</p></div>;
  }

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route 
            path="/onboarding" 
            element={user && !userProfile ? <OnboardingWizard /> : <Navigate to="/" replace />} 
          />
          <Route 
            path="/" 
            element={
              !user ? <LandingPage /> :
              !userProfile ? <Navigate to="/onboarding" replace /> :
              <Dashboard />
            } 
          />
          <Route path="/admin" element={<AdminDashboard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
