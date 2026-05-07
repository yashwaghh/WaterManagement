import React, { useState, useEffect, useCallback } from 'react';
import { Gift, CreditCard, ShoppingBag, Zap, Droplets, Award, Utensils, Shirt, Mail, CheckCircle2, X, RefreshCw } from 'lucide-react';
import useStore from '../../store/useStore';
import apiService from '../../services/api';

export default function StoreTab() {
  const { userProfile, user } = useStore();
  
  // Real balance from backend
  const [balance, setBalance] = useState(0);
  const [weeklyPoints, setWeeklyPoints] = useState(0);
  const [totalRedeemed, setTotalRedeemed] = useState(0);
  const [loadingBalance, setLoadingBalance] = useState(true);
  const [redeemError, setRedeemError] = useState('');
  
  // Modal State
  const [showModal, setShowModal] = useState(false);
  const [redeemedItem, setRedeemedItem] = useState(null);
  const [voucherCode, setVoucherCode] = useState("");
  const [isEmailing, setIsEmailing] = useState(false);

  // Fetch real points balance from backend
  const fetchBalance = useCallback(async () => {
    if (!userProfile?.flat_id) return;
    try {
      setLoadingBalance(true);
      const res = await apiService.getPoints(userProfile.flat_id);
      setBalance(res.data.balance);
      setWeeklyPoints(res.data.total_earned);
      setTotalRedeemed(res.data.total_redeemed);
    } catch (err) {
      console.error('Failed to fetch points balance:', err);
    } finally {
      setLoadingBalance(false);
    }
  }, [userProfile]);

  useEffect(() => {
    fetchBalance();
    // Refresh every 10s to stay in sync
    const interval = setInterval(fetchBalance, 10000);
    return () => clearInterval(interval);
  }, [fetchBalance]);

  // Generate Tiered Maintenance Discounts
  const maintenanceTiers = [5, 10, 15, 20, 25, 30, 35].map(percent => ({
    id: `maint-${percent}`,
    title: `${percent}% Maintenance Concession`,
    description: `Get ${percent}% off your next month's flat maintenance bill.`,
    cost: percent * 800, // 5% = 4000, 35% = 28000
    icon: <CreditCard size={32} className="text-blue-500" />,
    color: "from-blue-50 to-indigo-50 border-blue-200"
  }));

  // Lifestyle Rewards
  const lifestyleRewards = [
    {
      id: 'zomato-500',
      title: "₹500 Zomato Voucher",
      description: "Treat yourself! Redeemable on the Zomato app.",
      cost: 5000,
      icon: <Utensils size={32} className="text-red-500" />,
      color: "from-red-50 to-rose-50 border-red-200"
    },
    {
      id: 'tshirt-eco',
      title: "Eco-Warrior T-Shirt",
      description: "Exclusive organic cotton building merch.",
      cost: 4000,
      icon: <Shirt size={32} className="text-purple-500" />,
      color: "from-purple-50 to-pink-50 border-purple-200"
    },
    {
      id: 'plumber-service',
      title: "Free Plumbing Inspection",
      description: "One free basic plumbing check by maintenance.",
      cost: 3000,
      icon: <Droplets size={32} className="text-cyan-500" />,
      color: "from-cyan-50 to-blue-50 border-cyan-200"
    }
  ];

  const handleRedeem = async (item) => {
    if (!userProfile?.flat_id) return;
    if (balance < item.cost) return;

    setRedeemError('');
    try {
      const res = await apiService.redeemPoints(
        userProfile.flat_id,
        item.id,
        item.title,
        item.cost
      );

      // Update balance from server response
      setBalance(res.data.new_balance);
      setTotalRedeemed(prev => prev + item.cost);

      // Show success modal
      setRedeemedItem(item);
      const code = Math.random().toString(36).substring(2, 10).toUpperCase();
      setVoucherCode(`SDG-${code}`);
      setShowModal(true);
      setIsEmailing(true);
      
      setTimeout(() => {
        setIsEmailing(false);
      }, 2500);
    } catch (err) {
      const msg = err.response?.data?.error || 'Redemption failed. Please try again.';
      setRedeemError(msg);
      // Refresh balance in case it's stale
      fetchBalance();
    }
  };

  const renderItemCard = (item) => {
    const canAfford = balance >= item.cost;
    const progressPercent = Math.min(100, (balance / item.cost) * 100);
    
    return (
      <div key={item.id} className={`bg-gradient-to-br ${item.color} rounded-2xl border p-6 flex flex-col justify-between transition-transform hover:-translate-y-1 hover:shadow-lg`}>
        <div>
          <div className="flex justify-between items-start mb-4">
            <div className="p-3 bg-white rounded-xl shadow-sm">
              {item.icon}
            </div>
            <div className="bg-white px-3 py-1 rounded-full shadow-sm border border-gray-100 flex items-center gap-1 font-bold text-gray-800">
              <Zap size={14} className="text-amber-500" /> {item.cost.toLocaleString()}
            </div>
          </div>
          <h4 className="text-xl font-bold text-gray-900 mb-2">{item.title}</h4>
          <p className="text-gray-600 font-medium mb-6">{item.description}</p>
        </div>
        
        <div>
          {!canAfford && (
            <div className="mb-3">
              <div className="flex justify-between text-xs font-bold text-gray-500 mb-1">
                <span>Progress</span>
                <span>{progressPercent.toFixed(0)}%</span>
              </div>
              <div className="w-full bg-white rounded-full h-2">
                <div className="bg-indigo-500 h-2 rounded-full transition-all duration-1000" style={{ width: `${progressPercent}%` }}></div>
              </div>
            </div>
          )}
          
          <button 
            onClick={() => handleRedeem(item)}
            disabled={!canAfford || loadingBalance}
            className={`w-full py-3 rounded-xl font-bold transition-all ${
              canAfford 
                ? 'bg-gradient-to-r from-teal-500 to-cyan-600 text-white hover:from-teal-600 hover:to-cyan-700 shadow-md shadow-teal-500/20 transform hover:scale-[1.02] active:scale-[0.98]' 
                : 'bg-white text-gray-400 cursor-not-allowed border border-gray-200'
            }`}
          >
            {canAfford ? 'Redeem Reward' : `Need ${(item.cost - balance).toLocaleString()} more`}
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-8 animate-fade-in pb-12 relative">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-gray-100 pb-4">
        <div className="flex items-center gap-4">
          <div className="bg-gradient-to-br from-teal-400 to-cyan-500 p-4 rounded-2xl shadow-sm shadow-teal-500/20 text-white">
            <Gift size={28} />
          </div>
          <div>
            <h2 className="text-2xl font-extrabold text-gray-900 tracking-tight">Swag Store</h2>
            <p className="text-gray-500 font-medium">Redeem your hard-earned Reward Points</p>
          </div>
        </div>
        <button 
          onClick={fetchBalance} 
          disabled={loadingBalance}
          className="text-xs bg-teal-50 hover:bg-teal-100 text-teal-600 border border-teal-200 font-bold px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1.5"
        >
          <RefreshCw size={12} className={loadingBalance ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Error banner */}
      {redeemError && (
        <div className="flex items-center justify-between gap-3 rounded-xl bg-red-50 border border-red-200 px-5 py-3 text-red-800">
          <span className="font-medium text-sm">{redeemError}</span>
          <button onClick={() => setRedeemError('')} className="text-red-500 hover:text-red-700"><X size={16} /></button>
        </div>
      )}

      {/* Point Balance Hero */}
      <div className="bg-gradient-to-r from-teal-900 via-cyan-900 to-sky-900 rounded-3xl p-8 shadow-xl text-white relative overflow-hidden flex flex-col md:flex-row items-center justify-between border border-cyan-800/50">
        <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-400/20 rounded-full mix-blend-overlay filter blur-3xl opacity-60"></div>
        <div className="relative z-10">
          <p className="text-sm font-bold text-cyan-200 uppercase tracking-widest mb-1">Spendable Balance</p>
          <div className="flex items-center gap-3">
            <Zap size={40} className="text-amber-300 drop-shadow-md" />
            <h1 className="text-6xl font-black text-white tracking-tight drop-shadow-sm">
              {loadingBalance ? '...' : balance.toLocaleString()}
            </h1>
          </div>
          <div className="flex gap-4 mt-3 text-xs text-cyan-200/70">
            <span>Earned: {weeklyPoints.toLocaleString()}</span>
            <span>•</span>
            <span>Spent: {totalRedeemed.toLocaleString()}</span>
          </div>
        </div>
        <div className="mt-6 md:mt-0 relative z-10 bg-sky-900/40 backdrop-blur-md rounded-2xl p-6 border border-cyan-500/30 max-w-sm">
          <div className="flex items-start gap-3">
            <Award className="text-amber-300 shrink-0 filter drop-shadow-md" size={24} />
            <div>
              <p className="font-bold text-lg text-white mb-1">Keep saving to unlock more!</p>
              <p className="text-sm text-cyan-100/80 leading-relaxed">Maintain your daily eco-target streak to accumulate points faster. Points are awarded when admin resets the day.</p>
            </div>
          </div>
        </div>
      </div>

      {/* Maintenance Concessions Section */}
      <div>
        <h3 className="font-extrabold text-xl text-gray-900 mb-6 flex items-center gap-2">
          <CreditCard className="text-blue-500" /> Maintenance Concession Tiers
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {maintenanceTiers.map(renderItemCard)}
        </div>
      </div>

      {/* Lifestyle Rewards Section */}
      <div className="pt-8 border-t border-gray-100">
        <h3 className="font-extrabold text-xl text-gray-900 mb-6 flex items-center gap-2">
          <ShoppingBag className="text-purple-500" /> Lifestyle & Merch
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {lifestyleRewards.map(renderItemCard)}
        </div>
      </div>

      {/* Virtual Voucher Modal */}
      {showModal && redeemedItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/60 backdrop-blur-sm animate-fade-in">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden relative transform transition-all scale-100">
            {/* Close button */}
            <button 
              onClick={() => setShowModal(false)}
              className="absolute top-4 right-4 p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors z-10"
            >
              <X size={20} />
            </button>

            {/* Modal Header */}
            <div className={`bg-gradient-to-br ${redeemedItem.color} p-8 text-center relative`}>
              <div className="w-20 h-20 bg-white rounded-full shadow-lg flex items-center justify-center mx-auto mb-4 border-4 border-white">
                {redeemedItem.icon}
              </div>
              <h2 className="text-2xl font-black text-gray-900 mb-1">Redemption Successful!</h2>
              <p className="text-gray-700 font-medium">{redeemedItem.title}</p>
            </div>

            {/* Modal Body */}
            <div className="p-8">
              <div className="bg-gray-50 rounded-2xl p-6 border border-gray-200 border-dashed mb-6 text-center">
                <p className="text-sm font-bold text-gray-500 uppercase tracking-widest mb-2">Your Voucher Code</p>
                <div className="text-3xl font-black text-indigo-600 tracking-wider font-mono">
                  {voucherCode}
                </div>
              </div>

              {/* Email Status Indicator */}
              <div className="flex items-center justify-center gap-3 mb-6 p-4 rounded-xl bg-slate-50 border border-slate-100">
                {isEmailing ? (
                  <>
                    <Mail size={20} className="text-amber-500 animate-pulse" />
                    <span className="text-sm font-bold text-gray-600">Generating digital voucher and emailing to {user?.email || 'your inbox'}...</span>
                  </>
                ) : (
                  <>
                    <CheckCircle2 size={20} className="text-green-500" />
                    <span className="text-sm font-bold text-green-700">Voucher successfully sent to your email!</span>
                  </>
                )}
              </div>

              <button 
                onClick={() => setShowModal(false)}
                className="w-full bg-gradient-to-r from-teal-500 to-cyan-600 text-white font-bold py-3 rounded-xl hover:from-teal-600 hover:to-cyan-700 transition-colors shadow-md"
              >
                Close & Continue Saving
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
