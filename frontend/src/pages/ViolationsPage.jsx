import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  Search,
  Filter,
  Download,
  Eye,
  RefreshCw,
  Trash2,
  CheckCircle2,
  Calendar
} from 'lucide-react';
import ViolationBadge from '../components/ViolationBadge';
import EvidenceModal from '../components/EvidenceModal';
import { TrafficService } from '../services/services';

export default function ViolationsPage() {
  const [violations, setViolations] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);
  const [isLoading, setIsLoading] = useState(false);

  // Filters
  const [searchPlate, setSearchPlate] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [minSpeed, setMinSpeed] = useState('');

  const [selectedViolation, setSelectedViolation] = useState(null);

  const fetchViolations = async () => {
    setIsLoading(true);
    try {
      const params = {
        page: currentPage,
        page_size: pageSize,
      };
      if (searchPlate) params.plate_number = searchPlate;
      if (selectedType) params.violation_type = selectedType;
      if (selectedStatus) params.status = selectedStatus;
      if (minSpeed) params.min_speed = Number(minSpeed);

      const res = await TrafficService.getViolations(params);
      setViolations(res.items || []);
      setTotalCount(res.total || 0);
    } catch (err) {
      console.error('Failed to fetch violations:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchViolations();
  }, [currentPage, pageSize, selectedType, selectedStatus]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchViolations();
  };

  const handleResetFilters = () => {
    setSearchPlate('');
    setSelectedType('');
    setSelectedStatus('');
    setMinSpeed('');
    setCurrentPage(1);
    fetchViolations();
  };

  const totalPages = Math.ceil(totalCount / pageSize) || 1;

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-6 glass-card rounded-3xl border border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20 text-[11px] font-bold uppercase tracking-wider">
              Enforcement Log
            </span>
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Traffic Violation Registry
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Search, filter, inspect visual evidence, and verify automated traffic citations.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <a
            href={TrafficService.getViolationsCsvUrl()}
            download="violations.csv"
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors"
          >
            <Download className="w-4 h-4" />
            Export CSV
          </a>
          <button
            onClick={fetchViolations}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-4">
        <form onSubmit={handleSearchSubmit} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {/* Search Plate */}
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search Plate (e.g. AP39)..."
              value={searchPlate}
              onChange={(e) => setSearchPlate(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl pl-9 pr-3 py-2 text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          {/* Type Filter */}
          <div>
            <select
              value={selectedType}
              onChange={(e) => {
                setSelectedType(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
            >
              <option value="">All Offense Types</option>
              <option value="OVER_SPEEDING">Over Speeding</option>
              <option value="RED_LIGHT">Red Light Violation</option>
              <option value="WRONG_WAY">Wrong Way</option>
              <option value="LANE_VIOLATION">Lane Violation</option>
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <select
              value={selectedStatus}
              onChange={(e) => {
                setSelectedStatus(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
            >
              <option value="">All Enforcement Statuses</option>
              <option value="PENDING">Pending Review</option>
              <option value="CONFIRMED">Confirmed</option>
              <option value="DISMISSED">Dismissed</option>
            </select>
          </div>

          {/* Min Speed */}
          <div>
            <input
              type="number"
              placeholder="Min Speed (km/h)..."
              value={minSpeed}
              onChange={(e) => setMinSpeed(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          {/* Filter Buttons */}
          <div className="flex items-center gap-2">
            <button
              type="submit"
              className="flex-1 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold text-xs transition-colors"
            >
              Filter
            </button>
            <button
              type="button"
              onClick={handleResetFilters}
              className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 text-xs transition-colors"
            >
              Reset
            </button>
          </div>
        </form>
      </div>

      {/* Violations Table */}
      <div className="glass-card rounded-3xl p-6 border border-slate-800">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase text-[10px] tracking-wider">
                <th className="pb-3 px-4">Citation ID</th>
                <th className="pb-3 px-4">License Plate</th>
                <th className="pb-3 px-4">Vehicle Type</th>
                <th className="pb-3 px-4">Violation Type</th>
                <th className="pb-3 px-4">Speed / Limit</th>
                <th className="pb-3 px-4">Timestamp (UTC)</th>
                <th className="pb-3 px-4">Status</th>
                <th className="pb-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-850">
              {violations.length > 0 ? (
                violations.map((v) => (
                  <tr key={v.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-bold text-cyan-400">
                      #{v.id}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="font-mono font-bold text-white bg-slate-900 px-2.5 py-1 rounded-lg border border-slate-700">
                        {v.plate_number || 'UNKNOWN'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 uppercase text-slate-300 font-medium">
                      {v.vehicle?.vehicle_type || 'Car'}
                    </td>
                    <td className="py-3.5 px-4">
                      <ViolationBadge type={v.violation_type} size="sm" />
                    </td>
                    <td className="py-3.5 px-4 font-mono">
                      <span className="font-bold text-white text-sm">{v.speed}</span>{' '}
                      <span className="text-slate-500">/ {v.speed_limit} km/h</span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 font-mono text-[11px]">
                      {new Date(v.timestamp).toLocaleString()}
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
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
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => setSelectedViolation(v)}
                        className="px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-400 hover:text-cyan-300 font-semibold text-xs border border-slate-700 transition-colors inline-flex items-center gap-1.5"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        Evidence
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-500 text-xs">
                    {isLoading ? 'Loading violations...' : 'No violation records matching criteria found.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <div>
            Showing <b className="text-white">{violations.length}</b> of <b className="text-white">{totalCount}</b> total violations
          </div>
          <div className="flex items-center gap-2">
            <button
              disabled={currentPage <= 1}
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-white font-medium transition-colors"
            >
              Previous
            </button>
            <span className="px-3 py-1 font-mono text-cyan-400">
              Page {currentPage} of {totalPages}
            </span>
            <button
              disabled={currentPage >= totalPages}
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-white font-medium transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      {/* Evidence Modal */}
      {selectedViolation && (
        <EvidenceModal
          violation={selectedViolation}
          onClose={() => setSelectedViolation(null)}
          onUpdated={fetchViolations}
        />
      )}
    </div>
  );
}
