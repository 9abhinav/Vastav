import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Video,
  AlertTriangle,
  Car,
  BarChart3,
  Settings,
  ShieldCheck,
  Radio
} from 'lucide-react';

export default function Sidebar({ isStreaming, activeViolationsCount }) {
  const navItems = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/live', label: 'Live Monitoring', icon: Video, badge: isStreaming ? 'LIVE' : null, badgeColor: 'bg-red-500 text-white animate-pulse' },
    { to: '/violations', label: 'Violations', icon: AlertTriangle, badge: activeViolationsCount > 0 ? activeViolationsCount : null, badgeColor: 'bg-rose-600 text-white' },
    { to: '/vehicles', label: 'Vehicles Tracked', icon: Car },
    { to: '/analytics', label: 'Traffic Analytics', icon: BarChart3 },
    { to: '/settings', label: 'Settings & Calibration', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-surface/90 border-r border-surface-border flex flex-col h-screen sticky top-0 backdrop-blur-xl z-30">
      {/* Brand Header */}
      <div className="p-6 border-b border-surface-border flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center shadow-lg shadow-cyan-500/20 text-white">
          <ShieldCheck className="w-6 h-6" />
        </div>
        <div>
          <h1 className="font-extrabold text-lg tracking-wider text-white flex items-center gap-2">
            TRAFFIC<span className="text-cyan-400">AI</span>
          </h1>
          <p className="text-[11px] font-medium text-slate-400 uppercase tracking-widest">
            Violation Tracker
          </p>
        </div>
      </div>

      {/* Nav Links */}
      <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
          Main Console
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center justify-between px-3.5 py-3 rounded-xl font-medium text-sm transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/10 text-cyan-400 border border-cyan-500/30 shadow-lg shadow-cyan-500/10'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`
              }
            >
              <div className="flex items-center gap-3">
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${item.badgeColor}`}>
                  {item.badge}
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* System Status Footprint */}
      <div className="p-4 border-t border-surface-border m-3 rounded-2xl bg-surface-light/40 border border-slate-700/50">
        <div className="flex items-center justify-between text-xs mb-2">
          <span className="text-slate-400 flex items-center gap-1.5">
            <Radio className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
            AI Pipeline
          </span>
          <span className="text-emerald-400 font-semibold uppercase text-[11px]">Ready</span>
        </div>
        <div className="text-[11px] text-slate-500 flex justify-between">
          <span>YOLOv8 + ByteTrack</span>
          <span>v1.0</span>
        </div>
      </div>
    </aside>
  );
}
