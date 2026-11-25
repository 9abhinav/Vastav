import React, { useState } from 'react';
import { X, Download, CheckCircle, Clock, MapPin, Gauge, Car, AlertTriangle } from 'lucide-react';
import ViolationBadge from './ViolationBadge';
import { TrafficService } from '../services/services';

export default function EvidenceModal({ violation, onClose, onUpdated }) {
  const [status, setStatus] = useState(violation?.status || 'PENDING');
  const [isUpdating, setIsUpdating] = useState(false);

  if (!violation) return null;

  const handleStatusUpdate = async (newStatus) => {
    setIsUpdating(true);
    try {
      await TrafficService.updateViolation(violation.id, { status: newStatus });
      setStatus(newStatus);
      if (onUpdated) onUpdated();
    } catch (err) {
      console.error('Failed to update violation status:', err);
    } finally {
      setIsUpdating(false);
    }
  };

  const imageSrc = violation.evidence_path
    ? (violation.evidence_path.startsWith('http') || violation.evidence_path.startsWith('/')
        ? violation.evidence_path
        : `/${violation.evidence_path}`)
    : null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fadeIn">
      <div className="glass-card rounded-3xl w-full max-w-4xl max-h-[90vh] overflow-hidden border border-slate-700 shadow-2xl flex flex-col">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-surface-border flex items-center justify-between bg-surface/90">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-rose-500/20 border border-rose-500/30 flex items-center justify-center text-rose-400">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                Violation Evidence Record <span className="font-mono text-cyan-400">#{violation.id}</span>
              </h2>
              <p className="text-xs text-slate-400">
                Tracked Vehicle #{violation.tracking_id} • {new Date(violation.timestamp).toLocaleString()}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white flex items-center justify-center transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left: Snapshot Image */}
          <div className="lg:col-span-7 flex flex-col gap-3">
            <div className="relative rounded-2xl overflow-hidden bg-black/60 border border-slate-800 flex items-center justify-center min-h-[300px]">
              {imageSrc ? (
                <img
                  src={imageSrc}
                  alt={`Evidence for violation ${violation.id}`}
                  className="w-full h-auto object-contain rounded-xl"
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="250" viewBox="0 0 400 250"><rect width="400" height="250" fill="%23111827"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%2364748b" font-family="sans-serif" font-size="14">Evidence Snapshot Not Available</text></svg>';
                  }}
                />
              ) : (
                <div className="text-slate-500 text-sm flex flex-col items-center gap-2">
                  <AlertTriangle className="w-8 h-8 opacity-40" />
                  <span>No visual evidence snapshot found.</span>
                </div>
              )}
            </div>

            {imageSrc && (
              <a
                href={imageSrc}
                download={`violation_${violation.id}_evidence.jpg`}
                className="flex items-center justify-center gap-2 py-2 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 transition-colors"
              >
                <Download className="w-4 h-4" />
                Download High-Res Snapshot
              </a>
            )}
          </div>

          {/* Right: Telemetry & Enforcement Details */}
          <div className="lg:col-span-5 flex flex-col justify-between space-y-4">
            <div className="space-y-4">
              <div>
                <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1.5">
                  Violation Classification
                </label>
                <ViolationBadge type={violation.violation_type} size="md" />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                  <span className="text-[10px] text-slate-400 uppercase font-semibold flex items-center gap-1 mb-1">
                    <Gauge className="w-3 h-3 text-cyan-400" /> Recorded Speed
                  </span>
                  <p className="text-lg font-bold font-mono text-white">
                    {violation.speed} <span className="text-xs text-slate-400">km/h</span>
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                  <span className="text-[10px] text-slate-400 uppercase font-semibold flex items-center gap-1 mb-1">
                    <Gauge className="w-3 h-3 text-amber-400" /> Speed Limit
                  </span>
                  <p className="text-lg font-bold font-mono text-white">
                    {violation.speed_limit} <span className="text-xs text-slate-400">km/h</span>
                  </p>
                </div>
              </div>

              <div className="space-y-2.5 text-xs text-slate-300">
                <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-800/30">
                  <span className="text-slate-400 flex items-center gap-1.5">
                    <Car className="w-3.5 h-3.5 text-slate-400" /> Number Plate:
                  </span>
                  <span className="font-mono font-bold text-cyan-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-700">
                    {violation.plate_number || 'UNKNOWN'}
                  </span>
                </div>

                <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-800/30">
                  <span className="text-slate-400 flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" /> Location:
                  </span>
                  <span className="font-medium text-slate-200">{violation.location || 'Northbound Expressway - KM 14'}</span>
                </div>

                <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-800/30">
                  <span className="text-slate-400 flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-slate-400" /> Timestamp:
                  </span>
                  <span className="font-mono text-slate-300">{new Date(violation.timestamp).toUTCString()}</span>
                </div>
              </div>

              {violation.details && (
                <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 text-xs text-slate-400">
                  <span className="font-semibold text-slate-300 block mb-1">Incident Notes:</span>
                  {violation.details}
                </div>
              )}
            </div>

            {/* Enforcement Status Actions */}
            <div className="pt-4 border-t border-slate-800">
              <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
                Enforcement Decision
              </label>
              <div className="grid grid-cols-3 gap-2">
                <button
                  disabled={isUpdating}
                  onClick={() => handleStatusUpdate('CONFIRMED')}
                  className={`py-2 rounded-xl text-xs font-bold transition-all ${
                    status === 'CONFIRMED'
                      ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-600/30'
                      : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                  }`}
                >
                  CONFIRM
                </button>
                <button
                  disabled={isUpdating}
                  onClick={() => handleStatusUpdate('PENDING')}
                  className={`py-2 rounded-xl text-xs font-bold transition-all ${
                    status === 'PENDING'
                      ? 'bg-amber-600 text-white shadow-lg shadow-amber-600/30'
                      : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                  }`}
                >
                  PENDING
                </button>
                <button
                  disabled={isUpdating}
                  onClick={() => handleStatusUpdate('DISMISSED')}
                  className={`py-2 rounded-xl text-xs font-bold transition-all ${
                    status === 'DISMISSED'
                      ? 'bg-slate-600 text-white'
                      : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                  }`}
                >
                  DISMISS
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
