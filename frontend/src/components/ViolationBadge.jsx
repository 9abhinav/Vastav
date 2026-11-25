import React from 'react';
import { Gauge, ShieldAlert, Undo2, Spline } from 'lucide-react';

export default function ViolationBadge({ type, size = 'md' }) {
  const configs = {
    OVER_SPEEDING: {
      label: 'OVER SPEEDING',
      icon: Gauge,
      classes: 'bg-rose-500/15 text-rose-400 border-rose-500/30 glow-rose'
    },
    RED_LIGHT: {
      label: 'RED LIGHT VIOLATION',
      icon: ShieldAlert,
      classes: 'bg-red-500/15 text-red-400 border-red-500/30 glow-rose'
    },
    WRONG_WAY: {
      label: 'WRONG WAY',
      icon: Undo2,
      classes: 'bg-amber-500/15 text-amber-400 border-amber-500/30 glow-amber'
    },
    LANE_VIOLATION: {
      label: 'LANE VIOLATION',
      icon: Spline,
      classes: 'bg-violet-500/15 text-violet-400 border-violet-500/30'
    }
  };

  const config = configs[type] || {
    label: type || 'VIOLATION',
    icon: ShieldAlert,
    classes: 'bg-slate-700/40 text-slate-300 border-slate-600'
  };

  const Icon = config.icon;
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-[10px] gap-1' : 'px-3 py-1 text-xs gap-1.5';

  return (
    <span className={`inline-flex items-center rounded-lg font-bold border ${config.classes} ${sizeClasses}`}>
      <Icon className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />
      <span>{config.label}</span>
    </span>
  );
}
