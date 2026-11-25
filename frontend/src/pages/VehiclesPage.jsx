import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Car, Search, Filter, RefreshCw, Gauge, AlertTriangle, ArrowRight } from 'lucide-react';
import { TrafficService } from '../services/services';

export default function VehiclesPage() {
  const [vehicles, setVehicles] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);
  const [search, setSearch] = useState('');
  const [vehicleType, setVehicleType] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const navigate = useNavigate();

  const fetchVehicles = async () => {
    setIsLoading(true);
    try {
      const params = {
        page: currentPage,
        page_size: pageSize,
      };
      if (search) params.search = search;
      if (vehicleType) params.vehicle_type = vehicleType;

      const res = await TrafficService.getVehicles(params);
      setVehicles(res.items || []);
      setTotalCount(res.total || 0);
    } catch (err) {
      console.error('Failed to fetch vehicles:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchVehicles();
  }, [currentPage, pageSize, vehicleType]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchVehicles();
  };

  const totalPages = Math.ceil(totalCount / pageSize) || 1;

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-6 glass-card rounded-3xl border border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-[11px] font-bold uppercase tracking-wider">
              Fleet Intelligence
            </span>
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Tracked Vehicles Registry
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Historical vehicle registry, speed profiles, and violation histories.
          </p>
        </div>

        <button
          onClick={fetchVehicles}
          className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
          title="Refresh"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Filter Bar */}
      <div className="glass-card p-5 rounded-2xl border border-slate-800">
        <form onSubmit={handleSearchSubmit} className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search by Plate (e.g. MH02) or ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl pl-9 pr-3 py-2 text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <select
              value={vehicleType}
              onChange={(e) => {
                setVehicleType(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
            >
              <option value="">All Vehicle Classes</option>
              <option value="car">Car</option>
              <option value="motorcycle">Motorcycle</option>
              <option value="bus">Bus</option>
              <option value="truck">Truck</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="submit"
              className="flex-1 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold text-xs transition-colors"
            >
              Search
            </button>
            <button
              type="button"
              onClick={() => {
                setSearch('');
                setVehicleType('');
                setCurrentPage(1);
                fetchVehicles();
              }}
              className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 text-xs transition-colors"
            >
              Clear
            </button>
          </div>
        </form>
      </div>

      {/* Vehicles Table */}
      <div className="glass-card rounded-3xl p-6 border border-slate-800">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase text-[10px] tracking-wider">
                <th className="pb-3 px-4">Tracking ID</th>
                <th className="pb-3 px-4">License Plate</th>
                <th className="pb-3 px-4">Vehicle Type</th>
                <th className="pb-3 px-4">Avg Speed</th>
                <th className="pb-3 px-4">Peak Speed</th>
                <th className="pb-3 px-4">Violations</th>
                <th className="pb-3 px-4">First Detected</th>
                <th className="pb-3 px-4 text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-850">
              {vehicles.length > 0 ? (
                vehicles.map((v) => {
                  const violationCount = v.violations ? v.violations.length : 0;
                  return (
                    <tr
                      key={v.id}
                      onClick={() => navigate(`/vehicles/${v.id}`)}
                      className="hover:bg-slate-800/40 transition-colors cursor-pointer"
                    >
                      <td className="py-3.5 px-4 font-mono font-bold text-cyan-400">
                        #{v.tracking_id}
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="font-mono font-bold text-white bg-slate-900 px-2.5 py-1 rounded-lg border border-slate-700">
                          {v.plate_number || 'UNKNOWN'}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 uppercase text-slate-300 font-medium">
                        {v.vehicle_type}
                      </td>
                      <td className="py-3.5 px-4 font-mono text-slate-300">
                        {v.avg_speed} km/h
                      </td>
                      <td className="py-3.5 px-4 font-mono font-bold text-white">
                        {v.max_speed} km/h
                      </td>
                      <td className="py-3.5 px-4">
                        {violationCount > 0 ? (
                          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30">
                            {violationCount} Offenses
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400">
                            Clean
                          </span>
                        )}
                      </td>
                      <td className="py-3.5 px-4 text-slate-400 font-mono text-[11px]">
                        {new Date(v.first_seen).toLocaleTimeString()}
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-400">
                          <ArrowRight className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-500 text-xs">
                    {isLoading ? 'Loading vehicles...' : 'No vehicles found.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <div>
            Showing <b className="text-white">{vehicles.length}</b> of <b className="text-white">{totalCount}</b> total vehicles
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
    </div>
  );
}
