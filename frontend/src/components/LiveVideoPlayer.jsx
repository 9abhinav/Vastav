import React, { useState, useRef } from 'react';
import { Play, Square, Pause, Upload, Camera, Radio, Sparkles, RefreshCw } from 'lucide-react';
import { TrafficService } from '../services/services';

export default function LiveVideoPlayer({
  videoStatus,
  onStartProcessing,
  onStopProcessing,
  onPauseProcessing,
  onResumeProcessing
}) {
  const [sourceType, setSourceType] = useState('demo');
  const [webcamIndex, setWebcamIndex] = useState(0);
  const [rtspUrl, setRtspUrl] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const fileInputRef = useRef(null);

  const isProcessing = videoStatus?.status === 'PROCESSING';
  const isPaused = videoStatus?.status === 'PAUSED';

  const handleStart = () => {
    onStartProcessing({
      source_type: sourceType,
      webcam_index: Number(webcamIndex),
      rtsp_url: rtspUrl
    });
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadError(null);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await TrafficService.uploadVideo(formData);
      setIsUploading(false);
      onStartProcessing({
        source_type: 'upload',
        video_path: res.video_path
      });
    } catch (err) {
      setIsUploading(false);
      setUploadError(err.response?.data?.detail || 'Failed to upload video');
    }
  };

  return (
    <div className="glass-card rounded-3xl overflow-hidden border border-slate-800 shadow-2xl flex flex-col">
      {/* Stream Window Header */}
      <div className="px-6 py-3.5 border-b border-surface-border bg-slate-900/90 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
            <Radio className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              Optical Feed & Telemetry HUD
            </h2>
            <p className="text-[11px] text-slate-400">
              Multi-lane detection • Perspective speed estimation • ByteTrack active
            </p>
          </div>
        </div>

        {/* Live Status Badge */}
        <div className="flex items-center gap-2">
          <span
            className={`px-3 py-1 rounded-full text-[11px] font-bold tracking-wider uppercase border flex items-center gap-1.5 ${
              isProcessing
                ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30 glow-emerald'
                : isPaused
                ? 'bg-amber-500/15 text-amber-400 border-amber-500/30'
                : 'bg-slate-800 text-slate-400 border-slate-700'
            }`}
          >
            <span className={`w-2 h-2 rounded-full ${isProcessing ? 'bg-emerald-400 animate-ping' : 'bg-slate-500'}`} />
            {videoStatus?.status || 'IDLE'}
          </span>
        </div>
      </div>

      {/* Video Stream Area */}
      <div className="relative bg-black aspect-video flex items-center justify-center overflow-hidden">
        {isProcessing || isPaused ? (
          <img
            src="/api/video/stream"
            alt="Real-time Traffic Video Feed"
            className="w-full h-full object-contain"
          />
        ) : (
          <div className="flex flex-col items-center justify-center text-center p-8 max-w-md">
            <div className="w-16 h-16 rounded-3xl bg-slate-900 border border-slate-800 flex items-center justify-center text-cyan-400 mb-4 shadow-xl shadow-cyan-500/10">
              <Sparkles className="w-8 h-8" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Live Stream Offline</h3>
            <p className="text-xs text-slate-400 mb-6">
              Launch the built-in synthetic traffic demo or connect your local webcam / custom MP4 video to start detecting violations.
            </p>
            <button
              onClick={handleStart}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs tracking-wider uppercase shadow-lg shadow-cyan-500/25 transition-all transform active:scale-95 flex items-center gap-2"
            >
              <Play className="w-4 h-4 fill-current" />
              Launch Demo Stream
            </button>
          </div>
        )}

        {/* Floating Telemetry Info Overlay */}
        {(isProcessing || isPaused) && (
          <div className="absolute top-3 left-3 bg-slate-950/80 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-800 text-[11px] font-mono text-cyan-400 flex items-center gap-3">
            <span>TRACKING: <b className="text-white">{videoStatus.active_vehicles_count || 0}</b></span>
            <span>|</span>
            <span>TOTAL DETECTIONS: <b className="text-white">{videoStatus.total_vehicles_detected || 0}</b></span>
          </div>
        )}
      </div>

      {/* Stream Controls Toolbar */}
      <div className="p-4 bg-slate-900/95 border-t border-surface-border flex flex-wrap items-center justify-between gap-4">
        {/* Source Selector */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setSourceType('demo')}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              sourceType === 'demo'
                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 shadow-md shadow-cyan-500/10'
                : 'text-slate-400 hover:text-slate-200 bg-slate-800/60'
            }`}
          >
            Demo Video
          </button>

          <button
            onClick={() => {
              setSourceType('upload');
              fileInputRef.current?.click();
            }}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all ${
              sourceType === 'upload'
                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                : 'text-slate-400 hover:text-slate-200 bg-slate-800/60'
            }`}
          >
            <Upload className="w-3.5 h-3.5" />
            {isUploading ? 'Uploading...' : 'Upload MP4'}
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="video/*"
            className="hidden"
            onChange={handleFileUpload}
          />

          <button
            onClick={() => setSourceType('webcam')}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all ${
              sourceType === 'webcam'
                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                : 'text-slate-400 hover:text-slate-200 bg-slate-800/60'
            }`}
          >
            <Camera className="w-3.5 h-3.5" />
            Webcam
          </button>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          {!isProcessing && !isPaused ? (
            <button
              onClick={handleStart}
              className="flex items-center gap-2 px-5 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-slate-950 font-bold text-xs tracking-wider uppercase shadow-lg shadow-cyan-500/25 transition-transform active:scale-95"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              START
            </button>
          ) : (
            <>
              {isProcessing ? (
                <button
                  onClick={onPauseProcessing}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-slate-950 font-bold text-xs transition-colors"
                >
                  <Pause className="w-3.5 h-3.5 fill-current" />
                  PAUSE
                </button>
              ) : (
                <button
                  onClick={onResumeProcessing}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs transition-colors"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  RESUME
                </button>
              )}

              <button
                onClick={onStopProcessing}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-rose-600/80 hover:bg-rose-600 text-white font-bold text-xs border border-rose-500/30 transition-colors"
              >
                <Square className="w-3.5 h-3.5 fill-current" />
                STOP
              </button>
            </>
          )}
        </div>
      </div>

      {uploadError && (
        <div className="px-6 py-2 bg-rose-950/70 text-rose-300 text-xs border-t border-rose-800">
          {uploadError}
        </div>
      )}
    </div>
  );
}
