import React, { useState } from 'react';
import { signInWithEmailAndPassword, createUserWithEmailAndPassword } from 'firebase/auth';
import { auth } from '../../firebase';
import { useNavigate } from 'react-router-dom';
import { Droplet, Mail, Lock, ArrowRight, Loader2, Waves } from 'lucide-react';

// Animated falling water drops for the background
const FallingDrops = () => (
  <div className="absolute inset-0 overflow-hidden pointer-events-none z-[1]">
    {[...Array(12)].map((_, i) => (
      <div
        key={i}
        className="absolute text-cyan-400/20 animate-droplet"
        style={{
          left: `${5 + Math.random() * 90}%`,
          top: '-20px',
          animationDelay: `${i * 0.5}s`,
          animationDuration: `${2 + Math.random() * 2}s`,
          fontSize: `${12 + Math.random() * 14}px`,
        }}
      >
        💧
      </div>
    ))}
  </div>
);

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleAuth = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      if (isRegistering) {
        await createUserWithEmailAndPassword(auth, email, password);
      } else {
        await signInWithEmailAndPassword(auth, email, password);
      }
      navigate('/'); 
    } catch (err) {
      setError(err.message.replace('Firebase: ', '')); // cleaner error message
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center relative bg-slate-900">
      {/* Dynamic Background with CSS Gradients for a smoother look */}
      <div className="absolute inset-0 z-0 overflow-hidden">
        <div className="absolute -top-[30%] -left-[10%] w-[70%] h-[70%] rounded-full bg-cyan-600/20 blur-[120px]"></div>
        <div className="absolute top-[20%] -right-[20%] w-[60%] h-[60%] rounded-full bg-blue-600/20 blur-[120px]"></div>
        <div className="absolute -bottom-[20%] left-[20%] w-[80%] h-[70%] rounded-full bg-teal-600/20 blur-[150px]"></div>
        <div 
          className="absolute inset-0 opacity-15"
          style={{ backgroundImage: "url('https://images.unsplash.com/photo-1505118380757-91f5f5632de0?q=80&w=2070&auto=format&fit=crop')", backgroundSize: 'cover', backgroundPosition: 'center', mixBlendMode: 'overlay' }}
        ></div>
        <FallingDrops />
      </div>

      <div className="relative z-10 w-full max-w-md mx-4">
        {/* Main Card */}
        <div className="bg-slate-900/50 backdrop-blur-xl border border-white/10 rounded-3xl p-8 sm:p-10 shadow-2xl overflow-hidden relative">
          
          {/* Subtle top highlight */}
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent opacity-50"></div>

          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center p-4 bg-gradient-to-tr from-cyan-500 to-blue-600 rounded-2xl shadow-lg shadow-cyan-500/25 mb-6 ring-1 ring-white/20 transform transition-transform hover:scale-105 duration-300">
              <Droplet className="text-white fill-white/20" size={36} strokeWidth={2} />
            </div>
            <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-white mb-2">Aqua<span className="text-cyan-400">Sync</span></h1>
            <p className="text-slate-400 text-sm sm:text-base">
              {isRegistering ? 'Join the community and save water' : 'Sign in to monitor your water usage'}
            </p>
          </div>
          
          {error && (
            <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 flex items-start space-x-3">
              <div className="flex-1 text-sm text-red-200 leading-snug">{error}</div>
            </div>
          )}
          
          <form className="space-y-5" onSubmit={handleAuth}>
            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider ml-1">Email</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-cyan-400 transition-colors">
                  <Mail size={18} />
                </div>
                <input 
                  type="email" 
                  required 
                  placeholder="name@example.com" 
                  value={email} 
                  onChange={(e) => setEmail(e.target.value)} 
                  className="block w-full rounded-xl bg-slate-950/50 border border-slate-700/50 pl-11 pr-4 py-3.5 text-slate-100 placeholder-slate-500 focus:bg-slate-900 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 focus:outline-none transition-all duration-300" 
                />
              </div>
            </div>
            
            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider ml-1">Password</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-cyan-400 transition-colors">
                  <Lock size={18} />
                </div>
                <input 
                  type="password" 
                  required 
                  placeholder="••••••••" 
                  value={password} 
                  onChange={(e) => setPassword(e.target.value)} 
                  className="block w-full rounded-xl bg-slate-950/50 border border-slate-700/50 pl-11 pr-4 py-3.5 text-slate-100 placeholder-slate-500 focus:bg-slate-900 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 focus:outline-none transition-all duration-300" 
                />
              </div>
            </div>

            <button 
              type="submit" 
              disabled={isLoading}
              className="group relative flex w-full items-center justify-center space-x-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-500 px-4 py-3.5 text-sm font-bold text-white shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 hover:-translate-y-0.5 active:translate-y-0 transition-all duration-300 disabled:opacity-70 disabled:cursor-not-allowed disabled:hover:translate-y-0"
            >
              {isLoading ? (
                <Loader2 className="animate-spin" size={18} />
              ) : (
                <>
                  <span>{isRegistering ? 'Create Account' : 'Sign In'}</span>
                  <ArrowRight size={18} className="transition-transform group-hover:translate-x-1" />
                </>
              )}
            </button>
          </form>
          
          <div className="mt-8 relative flex items-center justify-center">
            <div className="absolute inset-x-0 h-px bg-slate-700/50"></div>
            <span className="relative bg-slate-900 px-4 text-xs text-slate-400 uppercase tracking-wider">
              or
            </span>
          </div>

          <div className="text-center mt-6">
            <button 
              type="button"
              onClick={() => {
                setIsRegistering(!isRegistering);
                setError('');
              }} 
              className="text-sm text-slate-400 hover:text-cyan-400 transition-colors focus:outline-none"
            >
              {isRegistering ? (
                <span>Already a member? <span className="font-semibold text-white">Log in</span></span>
              ) : (
                <span>Don't have an account? <span className="font-semibold text-white">Register</span></span>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
