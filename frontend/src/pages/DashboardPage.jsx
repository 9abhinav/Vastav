import React, { useState, useEffect } from 'react';
import {
  Car,
  AlertTriangle,
  Gauge,
  ShieldAlert,
  Undo2,
  Activity,
  ArrowUpRight,
  Eye,
  Radio
} from 'lucide-react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  AreaChart,
  Area
} from 'recharts';

import StatCard from '../components/StatCard';
import ViolationBadge from '../components/ViolationBadge';
import EvidenceModal from '../components/EvidenceModal';
import VirtualTrafficLightControl from '../components/VirtualTrafficLightControl';
import { TrafficService } from '../services/services';

const VIOLATION_COLORS = {
  OVER_SPEEDING: '#f43f5e',
  RED_LIGHT: '#ef4444',
  WRONG_WAY: '#f59e0b',
  LANE_VIOLATION: '#8b5cf6'
};

export default function DashboardPage({ telemetry, trafficLightState, onTrafficLightChange }) {
  const [stats, setStats] = useState(null);
  const [recentViolations, setRecentViolations] = useState([]);
  const [selectedViolation, setSelectedViolation] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchDashboardData = async () => {
    try {
      const [statsData, violationsData] = await Promise.all([
        TrafficService.getStats(),
        TrafficService.getViolations({ page: 1, page_size: 6 })
      ]);
      setStats(statsData);
      setRecentViolations(violationsData.items || []);
    } catch (err) {
      console.error('Error loading dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Top Welcome Banner */}
      <div className="glass-card rounded-3xl p-6 border border-slate-800 bg-gradient-to-r from-slate-900 via-slate-900/90 to-cyan-950/40 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-[11px] font-bold uppercase tracking-wider">
              Autonomous Enforcement Center
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
            Traffic Intelligence & Violation System
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time multi-lane monitoring, perspective velocity calibration, and automatic evidence capture.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right hidden sm:block">
            <span className="text-[10px] uppercase font-bold text-slate-400 block">Camera Feed Status</span>
            <span className="text-xs font-mono font-bold text-emerald-400">ONLINE (KM 14 North)</span>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Total Vehicles Tracked"
          value={stats?.total_vehicles || 0}
          subtitle={`Active in scene: ${telemetry?.active_vehicles_count || stats?.active_vehicles || 0}`}
          icon={Car}
          colorScheme="cyan"
          trend="+12% flow"
        />

        <StatCard
          title="Total Violations Logged"
          value={stats?.total_violations || 0}
          subtitle="Enforcement database"
          icon={AlertTriangle}
          colorScheme="rose"
          trend="Flagged"
        />

        <StatCard
          title="Over-Speeding Incidents"
          value={stats?.overspeeding_count || 0}
          subtitle={`Speed Limit: ${stats?.speed_limit || 60} km/h`}
          icon={Gauge}
          colorScheme="amber"
          trend="Critical"
        />

        <StatCard
          title="Red Light Breaches"
          value={stats?.red_light_count || 0}
          subtitle={`Signal: ${trafficLightState || 'GREEN'}`}
          icon={ShieldAlert}
          colorScheme="rose"
          trend="Automated"
        />
      </div>

      {/* Secondary Metrics & Quick Traffic Signal Control */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Quick Traffic Signal Switcher */}
        <div className="lg:col-span-4">
          <VirtualTrafficLightControl
            currentLightState={trafficLightState}
            onStateChange={onTrafficLightChange}
          />
        </div>

        {/* Speed & Flow Metrics Banner */}
        <div className="lg:col-span-8 glass-card rounded-3xl p-6 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-sm text-white flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-400" />
              Velocity & Violation Dynamics
            </h3>
            <span className="text-xs text-slate-400 font-mono">Real-time Homography</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-3.5 rounded-2xl bg-slate-900/60 border border-slate-800/80">
              <span className="text-[11px] text-slate-400 font-medium block">Average Speed</span>
              <p className="text-2xl font-extrabold text-white font-mono mt-1">
                {stats?.average_speed || 0} <span className="text-xs text-slate-400 font-normal">km/h</span>
              </p>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-900/60 border border-slate-800/80">
              <span className="text-[11px] text-slate-400 font-medium block">Peak Velocity</span>
              <p className="text-2xl font-extrabold text-rose-400 font-mono mt-1">
                {stats?.highest_recorded_speed || 0} <span className="text-xs text-slate-400 font-normal">km/h</span>
              </p>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-900/60 border border-slate-800/80">
              <span className="text-[11px] text-slate-400 font-medium block">Wrong-Way Driving</span>
              <p className="text-2xl font-extrabold text-amber-400 font-mono mt-1">
                {stats?.wrong_way_count || 0}
              </p>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-900/60 border border-slate-800/80">
              <span className="text-[11px] text-slate-400 font-medium block">Lane Violations</span>
              <p className="text-2xl font-extrabold text-violet-400 font-mono mt-1">
                {stats?.lane_violation_count || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Speed Distribution Bar Chart */}
        <div className="lg:col-span-7 glass-card rounded-3xl p-6 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-sm text-white">Vehicle Speed Distribution</h3>
              <p className="text-[11px] text-slate-400">Observed speed profiles across vehicle fleet</p>
            </div>
            <span className="text-xs font-mono text-cyan-400 bg-cyan-950/60 border border-cyan-900/80 px-2 py-0.5 rounded-lg">
              km/h Bins
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats?.speed_distribution || []}>
                <XAxis dataKey="range_label" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }}
                  itemStyle={{ color: '#22d3ee' }}
                />
                <Bar dataKey="count" fill="#06b6d4" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Violations by Type Pie Chart */}
        <div className="lg:col-span-5 glass-card rounded-3xl p-6 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-sm text-white">Violation Breakdown</h3>
              <p className="text-[11px] text-slate-400">Classification by offense type</p>
            </div>
          </div>

          <div className="h-64 w-full flex items-center justify-center">
            {stats?.violations_by_type && stats.violations_by_type.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={stats.violations_by_type}
                    dataKey="count"
                    nameKey="violation_type"
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={85}
                    paddingAngle={4}
                  >
                    {stats.violations_by_type.map((entry) => (
                      <Cell
                        key={entry.violation_type}
                        fill={VIOLATION_COLORS[entry.violation_type] || '#06b6d4'}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-slate-500 text-xs text-center">
                No violation incidents recorded yet.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Violation Incidents Table */}
      <div className="glass-card rounded-3xl p-6 border border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-bold text-sm text-white">Recent Enforced Violations</h3>
            <p className="text-[11px] text-slate-400">Live feed of automatically flagged traffic offenses</p>
          </div>
          <a
            href="/violations"
            className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 flex items-center gap-1 transition-colors"
          >
            View All Incidents <ArrowUpRight className="w-3.5 h-3.5" />
          </a>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase text-[10px] tracking-wider">
                <th className="pb-3 px-3">Violation ID</th>
                <th className="pb-3 px-3">Vehicle / Plate</th>
                <th className="pb-3 px-3">Offense Type</th>
                <th className="pb-3 px-3">Recorded Speed</th>
                <th className="pb-3 px-3">Timestamp</th>
                <th className="pb-3 px-3">Status</th>
                <th className="pb-3 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-850">
              {recentViolations.length > 0 ? (
                recentViolations.map((v) => (
                  <tr key={v.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-3 font-mono font-bold text-cyan-400">
                      #{v.id}
                    </td>
                    <td className="py-3 px-3">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-slate-100 bg-slate-900 px-2 py-0.5 rounded border border-slate-700">
                          {v.plate_number || 'UNKNOWN'}
                        </span>
                        <span className="text-slate-400 text-[11px]">#{v.tracking_id}</span>
                      </div>
                    </td>
                    <td className="py-3 px-3">
                      <ViolationBadge type={v.violation_type} size="sm" />
                    </td>
                    <td className="py-3 px-3 font-mono">
                      <span className="font-bold text-white">{v.speed}</span>{' '}
                      <span className="text-slate-500">/ {v.speed_limit} km/h</span>
                    </td>
                    <td className="py-3 px-3 text-slate-400 font-mono text-[11px]">
                      {new Date(v.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="py-3 px-3">
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          v.status === 'CONFIRMED'
                            ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                            : v.status === 'PENDING'
                            ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                            : 'bg-slate-700 text-slate-300'
                        }`}
                      >
                        {v.status}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-right">
                      <button
                        onClick={() => setSelectedViolation(v)}
                        className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white font-medium text-[11px] border border-slate-700 transition-colors inline-flex items-center gap-1"
                      >
                        <Eye className="w-3 h-3" />
                        Evidence
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500 text-xs">
                    No violation records logged yet. Start the video stream to begin real-time enforcement.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Evidence Modal */}
      {selectedViolation && (
        <EvidenceModal
          violation={selectedViolation}
          onClose={() => setSelectedViolation(null)}
          onUpdated={fetchDashboardData}
        />
      )}
    </div>
  );
}
