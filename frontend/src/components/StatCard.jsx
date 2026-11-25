import React from 'react';

export default function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  colorScheme = 'cyan' // 'cyan', 'rose', 'emerald', 'amber', 'violet'
}) {
  const colorMap = {
    cyan: {
      border: 'hover:border-cyan-500/50',
      bgIcon: 'from-cyan-500/20 to-blue-500/20 border-cyan-500/30 text-cyan-400',
      textAccent: 'text-cyan-400',
      glow: 'hover:shadow-cyan-500/10'
    },
    rose: {
      border: 'hover:border-rose-500/50',
      bgIcon: 'from-rose-500/20 to-pink-500/20 border-rose-500/30 text-rose-400',
      textAccent: 'text-rose-400',
      glow: 'hover:shadow-rose-500/10'
    },
    emerald: {
      border: 'hover:border-emerald-500/50',
      bgIcon: 'from-emerald-500/20 to-teal-500/20 border-emerald-500/30 text-emerald-400',
      textAccent: 'text-emerald-400',
      glow: 'hover:shadow-emerald-500/10'
    },
    amber: {
      border: 'hover:border-amber-500/50',
      bgIcon: 'from-amber-500/20 to-yellow-500/20 border-amber-500/30 text-amber-400',
      textAccent: 'text-amber-400',
      glow: 'hover:shadow-amber-500/10'
    },
    violet: {
      border: 'hover:border-violet-500/50',
      bgIcon: 'from-violet-500/20 to-purple-500/20 border-violet-500/30 text-violet-400',
      textAccent: 'text-violet-400',
      glow: 'hover:shadow-violet-500/10'
    }
  };

  const scheme = colorMap[colorScheme] || colorMap.cyan;

  return (
    <div className={`glass-card rounded-2xl p-5 transition-all duration-300 ${scheme.border} ${scheme.glow} hover:-translate-y-0.5`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
            {title}
          </p>
          <h3 className="text-3xl font-extrabold text-white tracking-tight font-mono">
            {value}
          </h3>
        </div>
        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${scheme.bgIcon} border flex items-center justify-center shadow-lg`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
        <span className="text-slate-400 font-medium">{subtitle}</span>
        {trend && (
          <span className={`font-semibold ${scheme.textAccent}`}>
            {trend}
          </span>
        )}
      </div>
    </div>
  );
}
