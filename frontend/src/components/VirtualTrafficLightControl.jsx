import React, { useState, useEffect } from 'react';
import { CircleDot, RefreshCw, Sliders } from 'lucide-react';
import { TrafficService } from '../services/services';

export default function VirtualTrafficLightControl({ currentLightState, onStateChange }) {
  const [autoCycle, setAutoCycle] = useState(false);
  const [cycleSeconds, setCycleSeconds] = useState(15);
  const [timer, setTimer] = useState(cycleSeconds);

  const states = ['GREEN', 'YELLOW', 'RED'];

  const handleStateClick = async (state) => {
    try {
      await TrafficService.setTrafficLight(state);
      if (onStateChange) onStateChange(state);
    } catch (err) {
      console.error('Error changing traffic light:', err);
    }
  };

  useEffect(() => {
    if (!autoCycle) return;

    const interval = setInterval(() => {
      setTimer((prev) => {
        if (prev <= 1) {
          // Advance state
          const currentIndex = states.indexOf(currentLightState || 'GREEN');
          const nextState = states[(currentIndex + 1) % states.length];
          handleStateClick(nextState);
          return cycleSeconds;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [autoCycle, currentLightState, cycleSeconds]);

  return (
    <div className="glass-card rounded-2xl p-5 border border-slate-800">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <CircleDot className="w-5 h-5 text-cyan-400" />
          <h3 className="font-bold text-sm text-white">Virtual Traffic Signal</h3>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setAutoCycle(!autoCycle)}
            className={`px-2.5 py-1 rounded-lg text-[11px] font-bold flex items-center gap-1.5 transition-all ${
              autoCycle
                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                : 'bg-slate-800 text-slate-400 hover:text-slate-200'
            }`}
          >
            <RefreshCw className={`w-3 h-3 ${autoCycle ? 'animate-spin' : ''}`} />
            {autoCycle ? `Auto (${timer}s)` : 'Manual Mode'}
          </button>
        </div>
      </div>

      {/* Traffic Signal Box Visual */}
      <div className="flex items-center justify-center gap-4 py-3 px-6 bg-slate-950/80 rounded-2xl border border-slate-800/80">
        {/* RED LAMP */}
        <button
          onClick={() => handleStateClick('RED')}
          className={`flex flex-col items-center gap-1.5 transition-transform active:scale-95 ${
            currentLightState === 'RED' ? 'scale-110' : 'opacity-40 hover:opacity-80'
          }`}
        >
          <div
            className={`w-12 h-12 rounded-full border-2 transition-all ${
              currentLightState === 'RED'
                ? 'bg-red-500 border-red-300 shadow-[0_0_25px_rgba(239,68,68,0.8)]'
                : 'bg-red-950 border-red-900'
            }`}
          />
          <span className="text-[10px] font-bold text-red-400 uppercase">Stop (Red)</span>
        </button>

        {/* YELLOW LAMP */}
        <button
          onClick={() => handleStateClick('YELLOW')}
          className={`flex flex-col items-center gap-1.5 transition-transform active:scale-95 ${
            currentLightState === 'YELLOW' ? 'scale-110' : 'opacity-40 hover:opacity-80'
          }`}
        >
          <div
            className={`w-12 h-12 rounded-full border-2 transition-all ${
              currentLightState === 'YELLOW'
                ? 'bg-amber-400 border-yellow-200 shadow-[0_0_25px_rgba(245,158,11,0.8)]'
                : 'bg-amber-950 border-amber-900'
            }`}
          />
          <span className="text-[10px] font-bold text-amber-400 uppercase">Wait (Yellow)</span>
        </button>

        {/* GREEN LAMP */}
        <button
          onClick={() => handleStateClick('GREEN')}
          className={`flex flex-col items-center gap-1.5 transition-transform active:scale-95 ${
            currentLightState === 'GREEN' ? 'scale-110' : 'opacity-40 hover:opacity-80'
          }`}
        >
          <div
            className={`w-12 h-12 rounded-full border-2 transition-all ${
              currentLightState === 'GREEN'
                ? 'bg-emerald-500 border-emerald-300 shadow-[0_0_25px_rgba(16,185,129,0.8)]'
                : 'bg-emerald-950 border-emerald-900'
            }`}
          />
          <span className="text-[10px] font-bold text-emerald-400 uppercase">Go (Green)</span>
        </button>
      </div>

      <p className="text-[11px] text-slate-500 mt-3 text-center">
        Vehicles crossing the virtual stop line while signal is <span className="text-rose-400 font-semibold">RED</span> trigger automatic Red Light violations.
      </p>
    </div>
  );
}
