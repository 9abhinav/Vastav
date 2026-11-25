import React, { useRef, useState, useEffect } from 'react';
import { Sliders, Save, RotateCcw, Crosshair, Check } from 'lucide-react';

export default function CalibrationCanvas({ settings, onSaveSettings }) {
  const canvasRef = useRef(null);
  const [activeTab, setActiveTab] = useState('calibration'); // 'calibration', 'stop_line', 'lanes'

  // Local editable copies
  const [sourcePoints, setSourcePoints] = useState(
    settings?.calibration?.source_points || [[200, 300], [1080, 300], [1200, 700], [80, 700]]
  );
  const [stopLine, setStopLine] = useState(
    settings?.stop_line || { x1: 100, y1: 500, x2: 1180, y2: 500 }
  );
  const [realWidth, setRealWidth] = useState(settings?.calibration?.real_world_width_meters || 8.0);
  const [realHeight, setRealHeight] = useState(settings?.calibration?.real_world_height_meters || 30.0);
  const [speedLimit, setSpeedLimit] = useState(settings?.speed_limit || 60.0);
  const [allowedDirection, setAllowedDirection] = useState(settings?.allowed_direction || 'down');
  const [saveSuccess, setSaveSuccess] = useState(false);

  const [draggedPointIndex, setDraggedPointIndex] = useState(null);
  const [draggedLineEnd, setDraggedLineEnd] = useState(null); // 'start', 'end'

  const canvasWidth = 800;
  const canvasHeight = 450;
  const scaleX = canvasWidth / 1280.0;
  const scaleY = canvasHeight / 720.0;

  // Redraw canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvasWidth, canvasHeight);

    // Background road simulation
    ctx.fillStyle = '#1e293b';
    ctx.fillRect(0, 0, canvasWidth, canvasHeight);

    // Draw grid
    ctx.strokeStyle = '#334155';
    ctx.lineWidth = 0.5;
    for (let x = 0; x < canvasWidth; x += 40) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvasHeight);
      ctx.stroke();
    }
    for (let y = 0; y < canvasHeight; y += 40) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvasWidth, y);
      ctx.stroke();
    }

    // 1. Draw Homography Polygon
    if (sourcePoints && sourcePoints.length === 4) {
      ctx.beginPath();
      const p0 = [sourcePoints[0][0] * scaleX, sourcePoints[0][1] * scaleY];
      ctx.moveTo(p0[0], p0[1]);
      for (let i = 1; i < 4; i++) {
        ctx.lineTo(sourcePoints[i][0] * scaleX, sourcePoints[i][1] * scaleY);
      }
      ctx.closePath();
      ctx.fillStyle = 'rgba(6, 182, 212, 0.15)';
      ctx.fill();
      ctx.strokeStyle = '#06b6d4';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Draw Corner Handles
      sourcePoints.forEach((pt, idx) => {
        const cx = pt[0] * scaleX;
        const cy = pt[1] * scaleY;
        ctx.beginPath();
        ctx.arc(cx, cy, 7, 0, 2 * Math.PI);
        ctx.fillStyle = draggedPointIndex === idx ? '#f43f5e' : '#22d3ee';
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.fillStyle = '#ffffff';
        ctx.font = '10px JetBrains Mono, monospace';
        ctx.fillText(`P${idx + 1}`, cx + 9, cy - 6);
      });
    }

    // 2. Draw Virtual Stop Line
    if (stopLine) {
      const sx1 = stopLine.x1 * scaleX;
      const sy1 = stopLine.y1 * scaleY;
      const sx2 = stopLine.x2 * scaleX;
      const sy2 = stopLine.y2 * scaleY;

      ctx.beginPath();
      ctx.moveTo(sx1, sy1);
      ctx.lineTo(sx2, sy2);
      ctx.strokeStyle = '#f43f5e';
      ctx.lineWidth = 3;
      ctx.stroke();

      // Stop Line handles
      [
        { x: sx1, y: sy1, key: 'start' },
        { x: sx2, y: sy2, key: 'end' }
      ].forEach((h) => {
        ctx.beginPath();
        ctx.arc(h.x, h.y, 6, 0, 2 * Math.PI);
        ctx.fillStyle = '#f43f5e';
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1.5;
        ctx.stroke();
      });

      ctx.fillStyle = '#f43f5e';
      ctx.font = 'bold 11px sans-serif';
      ctx.fillText('STOP LINE', sx1 + 10, sy1 - 8);
    }
  }, [sourcePoints, stopLine, draggedPointIndex, draggedLineEnd]);

  // Mouse drag handlers on canvas
  const handleMouseDown = (e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;

    if (activeTab === 'calibration') {
      // Check if clicking near calibration points
      for (let i = 0; i < sourcePoints.length; i++) {
        const px = sourcePoints[i][0] * scaleX;
        const py = sourcePoints[i][1] * scaleY;
        if (Math.hypot(mx - px, my - py) < 14) {
          setDraggedPointIndex(i);
          return;
        }
      }
    } else if (activeTab === 'stop_line') {
      const sx1 = stopLine.x1 * scaleX;
      const sy1 = stopLine.y1 * scaleY;
      const sx2 = stopLine.x2 * scaleX;
      const sy2 = stopLine.y2 * scaleY;

      if (Math.hypot(mx - sx1, my - sy1) < 14) {
        setDraggedLineEnd('start');
        return;
      }
      if (Math.hypot(mx - sx2, my - sy2) < 14) {
        setDraggedLineEnd('end');
        return;
      }
    }
  };

  const handleMouseMove = (e) => {
    if (draggedPointIndex === null && draggedLineEnd === null) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const mx = Math.max(0, Math.min(canvasWidth, e.clientX - rect.left));
    const my = Math.max(0, Math.min(canvasHeight, e.clientY - rect.top));

    const origX = mx / scaleX;
    const origY = my / scaleY;

    if (draggedPointIndex !== null) {
      const updated = [...sourcePoints];
      updated[draggedPointIndex] = [Math.round(origX), Math.round(origY)];
      setSourcePoints(updated);
    } else if (draggedLineEnd !== null) {
      if (draggedLineEnd === 'start') {
        setStopLine({ ...stopLine, x1: Math.round(origX), y1: Math.round(origY) });
      } else {
        setStopLine({ ...stopLine, x2: Math.round(origX), y2: Math.round(origY) });
      }
    }
  };

  const handleMouseUp = () => {
    setDraggedPointIndex(null);
    setDraggedLineEnd(null);
  };

  const handleSave = async () => {
    const updated = {
      ...settings,
      speed_limit: Number(speedLimit),
      allowed_direction: allowedDirection,
      stop_line: stopLine,
      calibration: {
        source_points: sourcePoints,
        real_world_width_meters: Number(realWidth),
        real_world_height_meters: Number(realHeight)
      }
    };
    await onSaveSettings(updated);
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 3000);
  };

  return (
    <div className="space-y-6">
      {/* Top Bar Tabs & Actions */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 bg-slate-900/80 rounded-2xl border border-slate-800">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab('calibration')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === 'calibration'
                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Homography Quad (Speed)
          </button>
          <button
            onClick={() => setActiveTab('stop_line')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === 'stop_line'
                ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Virtual Stop Line
          </button>
        </div>

        <button
          onClick={handleSave}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs tracking-wider uppercase shadow-lg shadow-cyan-500/20 transition-all active:scale-95"
        >
          {saveSuccess ? <Check className="w-4 h-4" /> : <Save className="w-4 h-4" />}
          {saveSuccess ? 'SAVED LIVE!' : 'SAVE CALIBRATION'}
        </button>
      </div>

      {/* Interactive Calibration Canvas */}
      <div className="glass-card p-6 rounded-3xl border border-slate-800">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-semibold text-slate-400">
            Drag the handles on the canvas below to adjust perspective coordinate mappings:
          </span>
          <span className="text-xs font-mono text-cyan-400">Resolution: 1280 x 720</span>
        </div>

        <div className="relative rounded-2xl overflow-hidden border border-slate-700 bg-slate-950 flex justify-center">
          <canvas
            ref={canvasRef}
            width={canvasWidth}
            height={canvasHeight}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            className="cursor-crosshair"
          />
        </div>
      </div>

      {/* Numerical Parameters Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card p-4 rounded-2xl">
          <label className="text-xs font-semibold text-slate-400 block mb-1.5">Speed Limit (km/h)</label>
          <input
            type="number"
            value={speedLimit}
            onChange={(e) => setSpeedLimit(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-white font-mono text-sm focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="glass-card p-4 rounded-2xl">
          <label className="text-xs font-semibold text-slate-400 block mb-1.5">Real Road Width (Meters)</label>
          <input
            type="number"
            step="0.5"
            value={realWidth}
            onChange={(e) => setRealWidth(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-white font-mono text-sm focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="glass-card p-4 rounded-2xl">
          <label className="text-xs font-semibold text-slate-400 block mb-1.5">Real Road Length (Meters)</label>
          <input
            type="number"
            step="1.0"
            value={realHeight}
            onChange={(e) => setRealHeight(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-white font-mono text-sm focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="glass-card p-4 rounded-2xl">
          <label className="text-xs font-semibold text-slate-400 block mb-1.5">Allowed Flow Direction</label>
          <select
            value={allowedDirection}
            onChange={(e) => setAllowedDirection(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-white text-sm focus:outline-none focus:border-cyan-500"
          >
            <option value="down">Downward (Southbound)</option>
            <option value="up">Upward (Northbound)</option>
            <option value="right">Rightward (Eastbound)</option>
            <option value="left">Leftward (Westbound)</option>
          </select>
        </div>
      </div>
    </div>
  );
}
