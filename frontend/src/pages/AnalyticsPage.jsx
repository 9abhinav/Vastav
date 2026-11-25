import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  TrendingUp,
  Activity,
  Car,
  PieChart as PieIcon,
  RefreshCw
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';
import { TrafficService } from '../services/services';

const VEHICLE_COLORS = ['#06b6d4', '#10b981', '#f59e0b', '#8b5cf6'];

export default function AnalyticsPage() {
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchStats = async () => {
    setIsLoading(true);
    try {
      const data = await TrafficService.getStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to load analytics:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-6 glass-card rounded-3xl border border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-[11px] font-bold uppercase tracking-wider">
              Deep Analytics
            </span>
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Traffic Intelligence & Enforcement Metrics
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Aggregate violation trends, speed curves, and vehicle classification insights.
          </p>
        </div>

        <button
          onClick={fetchStats}
          className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Top Trends Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Hourly Trend Chart */}
        <div className="lg:col-span-8 glass-card rounded-3xl p-6 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-sm text-white">Hourly Violation Distribution</h3>
              <p className="text-[11px] text-slate-400">Violation intensity across time windows</p>
            </div>
            <span className="text-xs font-mono text-cyan-400 bg-cyan-950/60 border border-cyan-900 px-2 py-0.5 rounded-lg">
              Last 6 Hours
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={stats?.hourly_trend || []}>
                <defs>
                  <linearGradient id="colorOverspeed" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#f43f5e" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorRedLight" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="hour" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }}
                />
                <Area type="monotone" dataKey="overspeeding" stroke="#f43f5e" fillOpacity={1} fill="url(#colorOverspeed)" />
                <Area type="monotone" dataKey="red_light" stroke="#ef4444" fillOpacity={1} fill="url(#colorRedLight)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Vehicle Classification Composition */}
        <div className="lg:col-span-4 glass-card rounded-3xl p-6 border border-slate-800 flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-sm text-white mb-1">Vehicle Classification Mix</h3>
            <p className="text-[11px] text-slate-400 mb-4">Proportion of detected vehicle types</p>

            <div className="h-56 w-full flex items-center justify-center">
              {stats?.vehicles_by_type && stats.vehicles_by_type.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={stats.vehicles_by_type}
                      dataKey="count"
                      nameKey="vehicle_type"
                      cx="50%"
                      cy="50%"
                      outerRadius={70}
                      label
                    >
                      {stats.vehicles_by_type.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={VEHICLE_COLORS[index % VEHICLE_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-slate-500 text-xs">No classification data recorded.</div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2 pt-4 border-t border-slate-800 text-xs">
            {stats?.vehicles_by_type?.map((v, i) => (
              <div key={v.vehicle_type} className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: VEHICLE_COLORS[i % VEHICLE_COLORS.length] }} />
                <span className="capitalize text-slate-300">{v.vehicle_type}:</span>
                <span className="font-mono font-bold text-white">{v.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
