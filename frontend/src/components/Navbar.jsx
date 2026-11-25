import React, { useState, useEffect } from 'react';
import { Play, Square, CircleDot, Activity, Clock } from 'lucide-react';
import { TrafficService } from '../services/services';

export default function Navbar({
  trafficLightState,
  onTrafficLightChange,
  videoStatus,
  onStartDemo,
  onStopProcessing
}) {
  const [timeStr, setTimeStr] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const isProcessing = videoStatus?.status === 'PROCESSING';

  return (
    <header className="h-20 border-b border-surface-border bg-surface/80 backdrop-blur-xl px-8 flex items-center justify-between sticky top-0 z-20">
      {/* Left: Stream Mode & Clock */}
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2.5">
          <div className={`w-3 h-3 rounded-full ${isProcessing ? 'bg-emerald-500 animate-ping' : 'bg-slate-600'}`} />
          <span className="text-xs font-bold tracking-wider uppercase text-slate-300">
            {isProcessing ? 'STREAM ACTIVE' : 'SYSTEM IDLE'}
          </span>
          {isProcessing && (
            <span className="text-[11px] font-mono text-cyan-400 bg-cyan-950/60 border border-cyan-800 px-2 py-0.5 rounded-full">
              {videoStatus.fps || 30} FPS
            </span>
          )}
        </div>

        <div className="hidden md:flex items-center gap-2 text-xs font-mono text-slate-400 bg-slate-800/40 px-3 py-1.5 rounded-lg border border-slate-700/50">
          <Clock className="w-3.5 h-3.5 text-slate-400" />
          <span>{timeStr}</span>
        </div>
      </div>

      {/* Right: Quick Controls */}
      <div className="flex items-center gap-4">
        {/* Virtual Traffic Light Indicator / Quick Switcher */}
        <div className="flex items-center gap-2 bg-slate-900/80 border border-slate-700/80 p-1.5 rounded-xl shadow-inner">
          <span className="text-[11px] font-semibold text-slate-400 px-2 uppercase tracking-wide">
            Signal:
          </span>
          <button
            onClick={() => onTrafficLightChange('RED')}
            className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
              trafficLightState === 'RED'
                ? 'bg-rose-600 text-white shadow-lg shadow-rose-600/40 scale-105'
                : 'text-rose-400 hover:bg-rose-950/40'
            }`}
          >
            RED
          </button>
          <button
            onClick={() => onTrafficLightChange('YELLOW')}
            className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
              trafficLightState === 'YELLOW'
                ? 'bg-amber-500 text-black shadow-lg shadow-amber-500/40 scale-105'
                : 'text-amber-400 hover:bg-amber-950/40'
            }`}
          >
            YELLOW
          </button>
          <button
            onClick={() => onTrafficLightChange('GREEN')}
            className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
              trafficLightState === 'GREEN'
                ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-600/40 scale-105'
                : 'text-emerald-400 hover:bg-emerald-950/40'
            }`}
          >
            GREEN
          </button>
        </div>

        {/* Start / Stop Demo Stream Button */}
        {!isProcessing ? (
          <button
            onClick={onStartDemo}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs tracking-wide shadow-lg shadow-cyan-500/25 transition-all transform active:scale-95"
          >
            <Play className="w-4 h-4 fill-current" />
            START DEMO
          </button>
        ) : (
          <button
            onClick={onStopProcessing}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-rose-600/80 hover:bg-rose-600 text-white font-bold text-xs tracking-wide border border-rose-500/40 shadow-lg shadow-rose-600/20 transition-all transform active:scale-95"
          >
            <Square className="w-4 h-4 fill-current" />
            STOP FEED
          </button>
        )}
      </div>
    </header>
  );
}
