import React from 'react';
import { Link } from 'react-router-dom';
import { Droplet, BarChart3, Trophy, ShieldCheck, ChevronRight, CheckCircle2, Waves } from 'lucide-react';

// Reusable SVG Wave Divider
const WaveDivider = ({ flip = false, color = '#f8fafc', opacity = 1 }) => (
  <div className={`w-full overflow-hidden leading-[0] ${flip ? 'rotate-180' : ''}`}>
    <svg viewBox="0 0 1440 120" preserveAspectRatio="none" className="w-full h-[60px] md:h-[80px]">
      <path
        d="M0,64L60,58.7C120,53,240,43,360,48C480,53,600,75,720,80C840,85,960,75,1080,64C1200,53,1320,43,1380,37.3L1440,32L1440,120L1380,120C1320,120,1200,120,1080,120C960,120,840,120,720,120C600,120,480,120,360,120C240,120,120,120,60,120L0,120Z"
        fill={color}
        fillOpacity={opacity}
      />
    </svg>
  </div>
);

// Floating water bubble particles
const WaterBubbles = () => (
  <div className="absolute inset-0 overflow-hidden pointer-events-none">
    {[...Array(8)].map((_, i) => (
      <div
        key={i}
        className="absolute rounded-full bg-cyan-400/10 border border-cyan-300/20 animate-bubble"
        style={{
          width: `${8 + Math.random() * 20}px`,
          height: `${8 + Math.random() * 20}px`,
          left: `${5 + Math.random() * 90}%`,
          bottom: '-20px',
          animationDelay: `${i * 0.7}s`,
          animationDuration: `${4 + Math.random() * 4}s`,
        }}
      />
    ))}
  </div>
);

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900 selection:bg-cyan-100 selection:text-cyan-900">
      {/* Navigation */}
      <nav className="fixed w-full z-50 bg-white/90 backdrop-blur-md border-b border-slate-200 transition-all duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <div className="bg-blue-600 p-2 rounded-lg">
                <Droplet className="text-white w-5 h-5" strokeWidth={2.5} />
              </div>
              <span className="text-xl font-bold tracking-tight text-slate-900">AquaSync</span>
            </div>
            <div className="hidden md:flex space-x-8 text-sm font-medium text-slate-600">
              <a href="#features" className="hover:text-blue-600 transition-colors">Features</a>
              <a href="#how-it-works" className="hover:text-blue-600 transition-colors">How it Works</a>
              <a href="#impact" className="hover:text-blue-600 transition-colors">Impact</a>
            </div>
            <div className="flex items-center space-x-4">
              <Link 
                to="/login"
                className="text-sm font-semibold text-slate-600 hover:text-slate-900 transition-colors"
              >
                Sign in
              </Link>
              <Link 
                to="/login"
                className="text-sm font-semibold bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg transition-colors shadow-sm"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden bg-gradient-to-b from-white via-cyan-50/30 to-white">
        {/* Subtle dot pattern */}
        <div className="absolute inset-0 z-0 opacity-[0.03]" style={{ backgroundImage: 'radial-gradient(#0f172a 1px, transparent 1px)', backgroundSize: '32px 32px' }}></div>
        {/* Animated water glow orbs */}
        <div className="absolute top-20 -left-32 w-96 h-96 bg-cyan-200/20 rounded-full blur-3xl animate-float opacity-60"></div>
        <div className="absolute bottom-10 -right-32 w-80 h-80 bg-blue-200/20 rounded-full blur-3xl animate-float-slow opacity-50"></div>
        <WaterBubbles />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-8 items-center">
            
            {/* Hero Copy */}
            <div className="max-w-2xl">
              <div className="inline-flex items-center space-x-2 bg-blue-50 text-blue-700 border border-blue-100 rounded-full px-3 py-1 mb-6 text-sm font-semibold">
                <span className="flex h-2 w-2 rounded-full bg-blue-600"></span>
                <span>SDG 6.4 Compliant Solution</span>
              </div>
              
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-slate-900 leading-[1.1] mb-6">
                Intelligent water management for <span className="text-water-gradient">modern communities.</span>
              </h1>
              
              <p className="text-lg text-slate-600 mb-8 leading-relaxed max-w-lg">
                Real-time metering, fair usage tracking, and community gamification to help residential complexes reduce water waste and build sustainable habits.
              </p>
              
              <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-4 sm:space-y-0 sm:space-x-4">
                <Link 
                  to="/login"
                  className="flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3.5 rounded-lg font-semibold shadow-sm transition-all w-full sm:w-auto"
                >
                  <span>Open Dashboard</span>
                  <ChevronRight size={18} />
                </Link>
                <div className="flex items-center space-x-2 text-sm text-slate-500 w-full justify-center sm:justify-start">
                  <CheckCircle2 className="text-emerald-500" size={16} />
                  <span>No credit card required for demo</span>
                </div>
              </div>
            </div>

            {/* Dashboard Mockup with Realistic Image Overlay */}
            <div className="relative hidden lg:block perspective-1000 mt-4">
              <div className="absolute inset-0 bg-blue-600/10 translate-y-6 translate-x-6 rounded-3xl blur-xl"></div>
              
              {/* High-quality contextual image */}
              <img 
                src="https://images.unsplash.com/photo-1468421870903-4df1664ac249?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80" 
                alt="Clean flowing water representing water management" 
                className="relative z-0 w-full h-[460px] object-cover rounded-3xl shadow-xl"
              />

              {/* Floating UI Card Overlay */}
              <div className="absolute -bottom-8 -left-8 z-10 bg-white/95 backdrop-blur-md border border-slate-200 rounded-2xl shadow-2xl p-6 w-[340px]">
                {/* Mockup Header */}
                <div className="flex items-center justify-between border-b border-slate-200 pb-4 mb-4">
                  <div className="flex space-x-2">
                    <div className="w-3 h-3 rounded-full bg-slate-300"></div>
                    <div className="w-3 h-3 rounded-full bg-slate-300"></div>
                    <div className="w-3 h-3 rounded-full bg-slate-300"></div>
                  </div>
                  <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Apt 4B Sensor</div>
                </div>
                {/* Mockup Content */}
                <div className="grid grid-cols-2 gap-3 mb-5">
                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                    <div className="text-xs text-slate-500 font-medium mb-1">Today's Usage</div>
                    <div className="text-xl font-bold text-slate-900">248<span className="text-xs font-normal text-slate-500 ml-1">L</span></div>
                  </div>
                  <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-100">
                    <div className="text-xs text-emerald-700 font-medium mb-1">Status</div>
                    <div className="flex items-center text-sm font-bold text-emerald-800">
                      Optimal Flow
                    </div>
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between text-xs text-slate-500 font-medium"><span>Kitchen</span><span>60%</span></div>
                  <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 w-[60%]"></div>
                  </div>
                  <div className="flex justify-between text-xs text-slate-500 font-medium pt-1"><span>Bathroom</span><span>40%</span></div>
                  <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                    <div className="h-full bg-cyan-400 w-[40%]"></div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      <WaveDivider color="#ffffff" />

      {/* Client Logos / Trusted By */}
      <section className="bg-white pt-8 pb-10 border-b border-slate-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-sm font-semibold text-slate-400 uppercase tracking-widest mb-6">Trusted by innovative property managers</p>
          <div className="flex flex-wrap justify-center gap-10 md:gap-20 opacity-50 grayscale hover:grayscale-0 focus-within:grayscale-0 transition-all duration-300">
            {/* Fake realistic company names styled as text logos */}
            <div className="flex items-center space-x-2"><div className="w-8 h-8 rounded bg-blue-600 text-white flex items-center justify-center font-bold">V</div><span className="text-xl font-bold text-slate-800">Veridian</span></div>
            <div className="flex items-center space-x-2"><Droplet className="text-cyan-600"/><span className="text-xl font-black text-slate-800">Oasis Real Estate</span></div>
            <div className="flex items-center space-x-2"><div className="w-8 h-8 rounded-full border-4 border-slate-800"></div><span className="text-xl font-semibold text-slate-800">Crescent Props</span></div>
            <div className="flex items-center space-x-2"><span className="text-xl font-serif italic font-bold text-slate-800">Elevate Living</span></div>
          </div>
        </div>
      </section>

      {/* Trust Metrics */}
      <section className="border-b border-slate-200 bg-gradient-to-r from-slate-50 via-cyan-50/40 to-slate-50 py-12 relative">
        <div className="absolute inset-0 opacity-[0.02]" style={{ backgroundImage: 'radial-gradient(#0891b2 1px, transparent 1px)', backgroundSize: '24px 24px' }}></div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center divide-x divide-slate-200">
            <div>
              <div className="text-3xl font-bold text-slate-900 mb-1">24/7</div>
              <div className="text-sm text-slate-500 font-medium">Real-time Monitoring</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-slate-900 mb-1">30%</div>
              <div className="text-sm text-slate-500 font-medium">Average Water Saved</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-slate-900 mb-1">Rewards</div>
              <div className="text-sm text-slate-500 font-medium">For Sustainable Habits</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-slate-900 mb-1">SDG 6.4</div>
              <div className="text-sm text-slate-500 font-medium">UN Efficiency Goal</div>
            </div>
          </div>
        </div>
      </section>

      <WaveDivider color="#ffffff" />

      {/* Features Section */}
      <section id="features" className="py-24 bg-white relative">
        <WaterBubbles />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Enterprise-grade infrastructure for <span className="text-water-gradient">everyday users.</span></h2>
            <p className="text-lg text-slate-600">Built to handle complex residential networks while providing a simple, intuitive dashboard for individual households.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-gradient-to-b from-white to-cyan-50/30 border border-slate-200 p-8 rounded-2xl shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
              <div className="bg-blue-100 w-12 h-12 rounded-xl flex items-center justify-center mb-6">
                <BarChart3 className="text-blue-700" size={24} />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-3">Granular Analytics</h3>
              <p className="text-slate-600 leading-relaxed">
                Track consumption down to the hour. Compare your usage against building averages and historical data to identify trends.
              </p>
            </div>
            
            <div className="bg-gradient-to-b from-white to-amber-50/30 border border-slate-200 p-8 rounded-2xl shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
              <div className="bg-amber-100 w-12 h-12 rounded-xl flex items-center justify-center mb-6">
                <Trophy className="text-amber-700" size={24} />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-3">Gamified Conservation</h3>
              <p className="text-slate-600 leading-relaxed">
                Earn Aqua Coins by staying under your daily water limit. Compete on the leaderboard and redeem points for real eco-friendly rewards.
              </p>
            </div>

            <div className="bg-gradient-to-b from-white to-emerald-50/30 border border-slate-200 p-8 rounded-2xl shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
              <div className="bg-emerald-100 w-12 h-12 rounded-xl flex items-center justify-center mb-6">
                <ShieldCheck className="text-emerald-700" size={24} />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-3">Secure & Transparent</h3>
              <p className="text-slate-600 leading-relaxed">
                Clear transparency on daily limits based on family size. Role-based access ensures equitable distribution among all residents.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonial / Social Proof */}
      <section className="py-24 bg-white border-t border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-blue-50 rounded-[2.5rem] p-8 md:p-12 lg:p-16 flex flex-col md:flex-row items-center md:space-x-12 relative overflow-hidden">
            {/* Background decoration */}
            <div className="absolute top-0 right-0 -mr-20 -mt-20 w-64 h-64 bg-blue-200/50 rounded-full blur-3xl"></div>
            
            <img 
              src="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80" 
              alt="Sarah Jenkins, Property Manager" 
              className="w-40 h-40 md:w-56 md:h-56 rounded-full object-cover shadow-2xl mb-8 md:mb-0 border-4 border-white relative z-10" 
            />
            
            <div className="relative z-10 text-center md:text-left">
              <div className="flex justify-center md:justify-start space-x-1 mb-6 text-amber-400">
                {[1,2,3,4,5].map(i => <svg key={i} className="w-5 h-5 fill-current" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" /></svg>)}
              </div>
              <p className="text-xl md:text-2xl font-medium text-slate-800 italic mb-6 leading-relaxed">
                "AquaSync helped our residential complex reduce overall water waste by 28% in just three months. 
                The gamified leaderboard completely shifted our community's mindset, turning water conservation into a fun, collective goal."
              </p>
              <div>
                <div className="text-lg font-bold text-slate-900">Sarah Jenkins</div>
                <div className="text-slate-600 font-medium">Head of Operations, Veridian Heights</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <WaveDivider color="#0c4a6e" />
      <section className="bg-gradient-to-b from-sky-900 to-cyan-950 py-20 relative overflow-hidden">
        <WaterBubbles />
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-6">Ready to optimize your <span className="text-cyan-300">water usage</span>?</h2>
          <p className="text-blue-200 text-lg mb-8 max-w-2xl mx-auto">
            Join the property managers and residents who are already using AquaSync to save money and protect our most vital resource.
          </p>
          <Link 
            to="/login"
            className="inline-flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4"
          >
             <button className="bg-white text-blue-900 hover:bg-blue-50 px-8 py-3.5 rounded-lg font-bold shadow-lg transition-colors w-full sm:w-auto">
              Access Dashboard
            </button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-950 pt-16 pb-8 border-t border-slate-800 text-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-12">
            <div className="col-span-2">
              <div className="flex items-center space-x-2 mb-4">
                <Droplet className="text-blue-500 w-5 h-5" />
                <span className="text-lg font-bold text-white tracking-tight">AquaSync</span>
              </div>
              <p className="text-slate-400 max-w-sm mb-6">
                Building sustainable communities through intelligent water monitoring and actionable insights.
              </p>
            </div>
            <div>
              <h4 className="text-slate-100 font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-slate-400">
                <li><a href="#" className="hover:text-blue-400 transition-colors">Features</a></li>
                <li><a href="#" className="hover:text-blue-400 transition-colors">Admin Dashboard</a></li>
                <li><a href="#" className="hover:text-blue-400 transition-colors">Hardware Setup</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-slate-100 font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-slate-400">
                <li><a href="#" className="hover:text-blue-400 transition-colors">About Us</a></li>
                <li><a href="#" className="hover:text-blue-400 transition-colors">SDG Goals</a></li>
                <li><a href="#" className="hover:text-blue-400 transition-colors">Contact</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row justify-between items-center text-slate-500">
            <p>© {new Date().getFullYear()} AquaSync Solutions. All rights reserved.</p>
            <div className="flex space-x-4 mt-4 md:mt-0">
              <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
              <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}