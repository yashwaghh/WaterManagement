import React, { useState } from 'react';
import { ref, set } from 'firebase/database';
import { db } from '../../firebase';
import { useNavigate } from 'react-router-dom';
import { useStore } from '../../store/useStore';
import { Droplet, Home, Users, CheckCircle2 } from 'lucide-react';

export default function OnboardingWizard() {
  const [flatId, setFlatId] = useState('A-101');
  const [familySize, setFamilySize] = useState(2);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();
  const setUserProfile = useStore(state => state.setUserProfile);
  const user = useStore(state => state.user);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!user) return;
    setIsSubmitting(true);

    const profileData = {
      flat_id: flatId,
      family_size: Number(familySize),
      onboarding_completed: true,
      created_at: new Date().toISOString()
    };

    try {
      await set(ref(db, `users/${user.uid}`), profileData);
      setUserProfile(profileData);
      navigate('/'); 
    } catch (error) {
      console.error("Error saving profile:", error);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center relative bg-slate-900">
      {/* Dynamic Background */}
      <div className="absolute inset-0 z-0 overflow-hidden">
        <div className="absolute top-[10%] -left-[10%] w-[60%] h-[60%] rounded-full bg-blue-600/10 blur-[120px]"></div>
        <div className="absolute bottom-[10%] -right-[10%] w-[60%] h-[60%] rounded-full bg-emerald-600/10 blur-[120px]"></div>
        <div 
          className="absolute inset-0 opacity-10"
          style={{ backgroundImage: "url('https://images.unsplash.com/photo-1505118380757-91f5f5632de0?q=80&w=2070&auto=format&fit=crop')", backgroundSize: 'cover', backgroundPosition: 'center', mixBlendMode: 'overlay' }}
        ></div>
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEgMWgydjJIMUMxeiIgZmlsbD0icmdiYSgyNTUsIDI1NSLCAyNTUsIDAuMDUpIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiLz48L3N2Zz4=')] [mask-image:linear-gradient(to_bottom,white,transparent)]"></div>
      </div>

      <div className="relative z-10 w-full max-w-lg mx-4">
        {/* Main Card */}
        <div className="bg-slate-900/60 backdrop-blur-xl border border-white/10 rounded-3xl p-8 sm:p-10 shadow-2xl overflow-hidden relative">
          
          <div className="absolute top-0 right-0 left-0 h-1 bg-gradient-to-r from-blue-500 via-cyan-400 to-emerald-400 opacity-60"></div>

          <div className="mb-8 text-center">
            <div className="inline-flex items-center justify-center p-4 bg-gradient-to-tr from-cyan-500 to-emerald-500 rounded-2xl shadow-lg shadow-emerald-500/25 mb-6 ring-1 ring-white/20">
              <Droplet className="text-white fill-white/20" size={36} strokeWidth={2} />
            </div>
            <h2 className="text-3xl font-black text-white tracking-tight">Setup Your <span className="text-cyan-400">Profile</span></h2>
            <p className="text-slate-400 mt-2 text-sm sm:text-base">Help us personalize your analytics</p>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-6 mt-6">
            
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider ml-1">Flat Unit</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-cyan-400 transition-colors">
                  <Home size={18} />
                </div>
                <select 
                  value={flatId} 
                  onChange={(e) => setFlatId(e.target.value)} 
                  className="block w-full rounded-xl bg-slate-950/50 border border-slate-700/50 pl-11 pr-10 py-3.5 text-slate-100 focus:bg-slate-900 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 focus:outline-none transition-all appearance-none scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent"
                >
                  <option value="A-101" className="bg-slate-900">A-101 (Real Sensor)</option>
                  <option value="A-102" className="bg-slate-900">A-102 (Simulated)</option>
                  <option value="A-103" className="bg-slate-900">A-103 (Simulated)</option>
                  <option value="A-104" className="bg-slate-900">A-104 (Simulated)</option>
                  <option value="B-201" className="bg-slate-900">B-201 (Simulated)</option>
                  <option value="B-202" className="bg-slate-900">B-202 (Simulated)</option>
                </select>
                <div className="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none text-slate-500">
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
                </div>
              </div>
            </div>
            
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider ml-1">Number of Residents</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-cyan-400 transition-colors">
                  <Users size={18} />
                </div>
                <input 
                  type="number" 
                  min="1" 
                  max="15" 
                  value={familySize} 
                  onChange={(e) => setFamilySize(e.target.value)} 
                  className="block w-full rounded-xl bg-slate-950/50 border border-slate-700/50 pl-11 pr-4 py-3.5 text-slate-100 placeholder-slate-500 focus:bg-slate-900 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 focus:outline-none transition-all" 
                />
              </div>
              <p className="text-xs text-slate-500 ml-1">Used to calculate your per-capita daily allowance.</p>
            </div>

            <div className="pt-4">
              <button 
                type="submit" 
                disabled={isSubmitting}
                className="group relative flex w-full items-center justify-center space-x-2 rounded-xl bg-gradient-to-r from-cyan-500 to-emerald-500 px-4 py-3.5 text-sm font-bold text-white shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40 hover:-translate-y-0.5 active:translate-y-0 transition-all duration-300 disabled:opacity-70 disabled:cursor-not-allowed disabled:hover:translate-y-0"
              >
                {isSubmitting ? (
                  <span className="flex items-center space-x-2">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                    Saving...
                  </span>
                ) : (
                  <>
                    <span>Complete Setup</span>
                    <CheckCircle2 size={18} className="transition-transform group-hover:scale-110" />
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
