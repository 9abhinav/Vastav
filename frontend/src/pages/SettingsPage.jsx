import React, { useState, useEffect } from 'react';
import { Settings, Sliders, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';
import CalibrationCanvas from '../components/CalibrationCanvas';
import { TrafficService } from '../services/services';

export default function SettingsPage() {
  const [settings, setSettings] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);

  const fetchSettings = async () => {
    setIsLoading(true);
    try {
      const data = await TrafficService.getSettings();
      setSettings(data);
    } catch (err) {
      console.error('Failed to load settings:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleSaveSettings = async (updatedSettings) => {
    setIsSaving(true);
    setStatusMessage(null);
    try {
      const saved = await TrafficService.updateSettings(updatedSettings);
      setSettings(saved);
      setStatusMessage({ type: 'success', text: 'System configuration and calibration saved successfully!' });
    } catch (err) {
      setStatusMessage({ type: 'error', text: 'Failed to update system settings.' });
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px] text-slate-500 text-sm">
        Loading system configuration...
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-6 glass-card rounded-3xl border border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-[11px] font-bold uppercase tracking-wider">
              Control Center
            </span>
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            System Settings & Optical Calibration
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Configure homography perspective matrices, virtual stop lines, speed thresholds, and OCR parameters.
          </p>
        </div>

        <button
          onClick={fetchSettings}
          className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {statusMessage && (
        <div
          className={`p-4 rounded-2xl text-xs font-semibold flex items-center gap-2 ${
            statusMessage.type === 'success'
              ? 'bg-emerald-950/80 border border-emerald-800 text-emerald-300'
              : 'bg-rose-950/80 border border-rose-800 text-rose-300'
          }`}
        >
          {statusMessage.type === 'success' ? <CheckCircle2 className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
          {statusMessage.text}
        </div>
      )}

      {/* Interactive Calibration & Parameter Editor */}
      <CalibrationCanvas
        settings={settings}
        onSaveSettings={handleSaveSettings}
      />
    </div>
  );
}
