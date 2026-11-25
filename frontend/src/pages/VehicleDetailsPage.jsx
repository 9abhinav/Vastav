import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Car,
  Gauge,
  AlertTriangle,
  Clock,
  MapPin,
  Calendar,
  ShieldCheck,
  Eye
} from 'lucide-react';
import ViolationBadge from '../components/ViolationBadge';
import EvidenceModal from '../components/EvidenceModal';
import { TrafficService } from '../services/services';

export default function VehicleDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [vehicle, setVehicle] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedViolation, setSelectedViolation] = useState(null);

  const fetchVehicleDetails = async () => {
    setIsLoading(true);
    try {
      const data = await TrafficService.getVehicle(id);
      setVehicle(data);
    } catch (err) {
      console.error('Failed to load vehicle details:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchVehicleDetails();
  }, [id]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px] text-slate-500 text-sm">
        Loading vehicle profile...
      </div>
    );
  }

  if (!vehicle) {
    return (
      <div className="p-8 text-center glass-card rounded-3xl">
        <h2 className="text-lg font-bold text-white mb-2">Vehicle Not Found</h2>
        <button
          onClick={() => navigate('/vehicles')}
          className="px-4 py-2 rounded-xl bg-slate-800 text-cyan-400 text-xs font-semibold"
        >
          Back to Vehicles Registry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Back Button */}
      <button
        onClick={() => navigate('/vehicles')}
        className="flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Vehicles Registry
      </button>

      {/* Vehicle Profile Card */}
      <div className="glass-card rounded-3xl p-6 border border-slate-800 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-xl">
            <Car className="w-8 h-8" />
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="font-mono text-xs font-bold text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800">
                Track #{vehicle.tracking_id}
              </span>
              <span className="text-xs uppercase font-bold text-slate-400">
                {vehicle.vehicle_type}
              </span>
            </div>
            <h1 className="text-3xl font-extrabold text-white font-mono tracking-tight">
              {vehicle.plate_number || 'UNKNOWN'}
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="px-4 py-2 rounded-xl bg-slate-900/80 border border-slate-800 text-right">
            <span className="text-[10px] uppercase font-bold text-slate-400 block">Detections</span>
            <span className="text-base font-bold font-mono text-cyan-400">{vehicle.total_detections} frames</span>
          </div>
        </div>
      </div>

      {/* Telemetry Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card p-5 rounded-2xl">
          <span className="text-xs text-slate-400 font-medium block">Average Speed</span>
          <p className="text-2xl font-bold font-mono text-white mt-1">
            {vehicle.avg_speed} <span className="text-xs text-slate-400">km/h</span>
          </p>
        </div>

        <div className="glass-card p-5 rounded-2xl">
          <span className="text-xs text-slate-400 font-medium block">Maximum Peak Speed</span>
          <p className="text-2xl font-bold font-mono text-rose-400 mt-1">
            {vehicle.max_speed} <span className="text-xs text-slate-400">km/h</span>
          </p>
        </div>

        <div className="glass-card p-5 rounded-2xl">
          <span className="text-xs text-slate-400 font-medium block">First Detected</span>
          <p className="text-xs font-mono text-slate-200 mt-2">
            {new Date(vehicle.first_seen).toLocaleString()}
          </p>
        </div>

        <div className="glass-card p-5 rounded-2xl">
          <span className="text-xs text-slate-400 font-medium block">Last Observed</span>
          <p className="text-xs font-mono text-slate-200 mt-2">
            {new Date(vehicle.last_seen).toLocaleString()}
          </p>
        </div>
      </div>

      {/* Violations History Section */}
      <div className="glass-card rounded-3xl p-6 border border-slate-800">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="font-bold text-base text-white">Violation Enforcement History</h3>
            <p className="text-xs text-slate-400">All citations automatically flagged for this vehicle</p>
          </div>
          <span className="px-3 py-1 rounded-full text-xs font-bold font-mono bg-rose-500/15 text-rose-400 border border-rose-500/30">
            {vehicle.violations?.length || 0} Citations
          </span>
        </div>

        {vehicle.violations && vehicle.violations.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {vehicle.violations.map((v) => (
              <div
                key={v.id}
                className="p-4 rounded-2xl bg-slate-900/70 border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between space-y-3"
              >
                <div className="flex items-center justify-between">
                  <ViolationBadge type={v.violation_type} size="sm" />
                  <span className="text-xs font-mono text-slate-400">
                    {new Date(v.timestamp).toLocaleTimeString()}
                  </span>
                </div>

                <div className="flex items-center justify-between text-xs text-slate-300">
                  <span>Recorded Speed:</span>
                  <span className="font-bold font-mono text-rose-400 text-sm">
                    {v.speed} km/h
                  </span>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-slate-800">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                    v.status === 'CONFIRMED' ? 'bg-emerald-950 text-emerald-400' : 'bg-amber-950 text-amber-400'
                  }`}>
                    {v.status}
                  </span>

                  <button
                    onClick={() => setSelectedViolation(v)}
                    className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-400 text-xs font-semibold inline-flex items-center gap-1"
                  >
                    <Eye className="w-3.5 h-3.5" /> Inspect Evidence
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-12 text-center text-slate-500 text-xs">
            <ShieldCheck className="w-10 h-10 mx-auto text-emerald-400 mb-2 opacity-50" />
            <p>No traffic violations registered for this vehicle. Clean driving history.</p>
          </div>
        )}
      </div>

      {/* Evidence Modal */}
      {selectedViolation && (
        <EvidenceModal
          violation={selectedViolation}
          onClose={() => setSelectedViolation(null)}
          onUpdated={fetchVehicleDetails}
        />
      )}
    </div>
  );
}
