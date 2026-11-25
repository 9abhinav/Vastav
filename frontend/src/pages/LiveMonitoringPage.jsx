import React, { useState } from 'react';
import {
  Radio,
  Car,
  Gauge,
  ShieldAlert,
  AlertCircle,
  Clock,
  Eye,
  Volume2,
  VolumeX
} from 'lucide-react';
import LiveVideoPlayer from '../components/LiveVideoPlayer';
import VirtualTrafficLightControl from '../components/VirtualTrafficLightControl';
import ViolationBadge from '../components/ViolationBadge';
import EvidenceModal from '../components/EvidenceModal';

export default function LiveMonitoringPage({
  videoStatus,
  telemetry,
  trafficLightState,
  onTrafficLightChange,
  onStartProcessing,
  onStopProcessing,
  onPauseProcessing,
  onResumeProcessing
}) {
  const [selectedViolation, setSelectedViolation] = useState(null);
  const [soundEnabled, setSoundEnabled] = useState(false);

  const activeVehicles = telemetry?.vehicles || [];
  const latestViolations = telemetry?.new_violations || [];

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 glass-card rounded-3xl border border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center text-slate-950 font-extrabold shadow-lg shadow-cyan-500/20">
            <Radio className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Live Monitoring Console</h1>
            <p className="text-xs text-slate-400">
              Synchronized optical feed, AI tracking matrix, and live telemetry broadcast.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setSoundEnabled(!soundEnabled)}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 border transition-all ${
              soundEnabled
                ? 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30'
                : 'bg-slate-800 text-slate-400 border-slate-700'
            }`}
          >
            {soundEnabled ? <Volume2 className="w-3.5 h-3.5" /> : <VolumeX className="w-3.5 h-3.5" />}
            {soundEnabled ? 'Audio Alerts: ON' : 'Audio Alerts: OFF'}
          </button>
        </div>
      </div>

      {/* Main Grid: Stream Player + Side Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Video Player */}
        <div className="lg:col-span-8 space-y-6">
          <LiveVideoPlayer
            videoStatus={videoStatus}
            onStartProcessing={onStartProcessing}
            onStopProcessing={onStopProcessing}
            onPauseProcessing={onPauseProcessing}
            onResumeProcessing={onResumeProcessing}
          />

          {/* Active Tracked Vehicles Table */}
          <div className="glass-card rounded-3xl p-6 border border-slate-800">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Car className="w-4 h-4 text-cyan-400" />
                <h3 className="font-bold text-sm text-white">
                  Active Vehicles in Optical View ({activeVehicles.length})
                </h3>
              </div>
              <span className="text-xs font-mono text-slate-400">Live Frame Matrix</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase text-[10px] tracking-wider">
                    <th className="pb-3 px-3">Vehicle ID</th>
                    <th className="pb-3 px-3">Classification</th>
                    <th className="pb-3 px-3">License Plate</th>
                    <th className="pb-3 px-3">Current Speed</th>
                    <th className="pb-3 px-3">Peak Speed</th>
                    <th className="pb-3 px-3">Status / Violations</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-850">
                  {activeVehicles.length > 0 ? (
                    activeVehicles.map((v) => {
                      const isOverspeed = v.current_speed > 60;
                      const hasViolation = v.active_violations && v.active_violations.length > 0;
                      return (
                        <tr key={v.track_id} className="hover:bg-slate-800/40 transition-colors">
                          <td className="py-2.5 px-3 font-mono font-bold text-cyan-400">
                            #{v.track_id}
                          </td>
                          <td className="py-2.5 px-3 uppercase text-slate-300 font-medium">
                            {v.class_name}
                          </td>
                          <td className="py-2.5 px-3">
                            <span className="font-mono font-bold text-white bg-slate-900 px-2 py-0.5 rounded border border-slate-700">
                              {v.plate_number || 'UNKNOWN'}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 font-mono">
                            <span className={`font-bold ${isOverspeed ? 'text-rose-400' : 'text-emerald-400'}`}>
                              {v.current_speed}
                            </span>{' '}
                            <span className="text-slate-500">km/h</span>
                          </td>
                          <td className="py-2.5 px-3 font-mono text-slate-400">
                            {v.max_speed} km/h
                          </td>
                          <td className="py-2.5 px-3">
                            {hasViolation ? (
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30 glow-rose">
                                <AlertCircle className="w-3 h-3" />
                                {v.active_violations.join(', ')}
                              </span>
                            ) : isOverspeed ? (
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30">
                                OVERSPEED
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                                NORMAL
                              </span>
                            )}
                          </td>
                        </tr>
                      );
                    })
                  ) : (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-slate-500 text-xs">
                        No vehicles currently inside the camera detection zone.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right: Controls & Real-time Alerts Feed */}
        <div className="lg:col-span-4 space-y-6">
          {/* Virtual Traffic Light Quick Control */}
          <VirtualTrafficLightControl
            currentLightState={trafficLightState}
            onStateChange={onTrafficLightChange}
          />

          {/* Real-time Alerts Live Feed */}
          <div className="glass-card rounded-3xl p-6 border border-slate-800 flex flex-col h-[520px]">
            <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-rose-400" />
                <h3 className="font-bold text-sm text-white">Live Violation Ticker</h3>
              </div>
              <span className="text-[10px] uppercase font-bold text-rose-400 bg-rose-950/60 border border-rose-800 px-2 py-0.5 rounded-full">
                Broadcast Feed
              </span>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3 pr-1">
              {latestViolations.length > 0 ? (
                latestViolations.map((viol, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 rounded-2xl bg-slate-900/80 border border-rose-500/30 hover:border-rose-400 transition-all cursor-pointer shadow-lg shadow-rose-500/5 animate-slideDown"
                    onClick={() => setSelectedViolation(viol)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <ViolationBadge type={viol.violation_type} size="sm" />
                      <span className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
                        <Clock className="w-3 h-3" /> Just now
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-xs mt-1">
                      <span className="text-slate-300">
                        Vehicle <b className="text-white">#{viol.track_id}</b> ({viol.vehicle_type || 'Car'})
                      </span>
                      <span className="font-mono font-bold text-rose-400">
                        {viol.speed} km/h
                      </span>
                    </div>

                    {viol.plate_number && viol.plate_number !== 'UNKNOWN' && (
                      <div className="mt-2 text-[11px] text-cyan-400 font-mono">
                        Plate: {viol.plate_number}
                      </div>
                    )}

                    <div className="mt-2.5 pt-2 border-t border-slate-800 flex justify-between items-center text-[10px] text-slate-400">
                      <span>Click to inspect snapshot</span>
                      <Eye className="w-3 h-3 text-cyan-400" />
                    </div>
                  </div>
                ))
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-500 text-xs">
                  <ShieldAlert className="w-8 h-8 mb-2 opacity-30 text-slate-400" />
                  <span>Waiting for violation events...</span>
                  <span className="text-[10px] text-slate-600 mt-1">
                    Violations will appear here in real-time as detected by YOLO and homography estimators.
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Evidence Modal */}
      {selectedViolation && (
        <EvidenceModal
          violation={selectedViolation}
          onClose={() => setSelectedViolation(null)}
        />
      )}
    </div>
  );
}
