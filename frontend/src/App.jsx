import React, { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';

import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import DashboardPage from './pages/DashboardPage';
import LiveMonitoringPage from './pages/LiveMonitoringPage';
import ViolationsPage from './pages/ViolationsPage';
import VehiclesPage from './pages/VehiclesPage';
import VehicleDetailsPage from './pages/VehicleDetailsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import SettingsPage from './pages/SettingsPage';

import { TrafficService } from './services/services';
import { telemetryWS } from './services/websocket';

export default function App() {
  const [videoStatus, setVideoStatus] = useState(null);
  const [telemetry, setTelemetry] = useState(null);
  const [trafficLightState, setTrafficLightState] = useState('GREEN');

  // Load initial video status & traffic light state
  const syncStatus = async () => {
    try {
      const status = await TrafficService.getVideoStatus();
      setVideoStatus(status);
      if (status.traffic_light_state) {
        setTrafficLightState(status.traffic_light_state);
      }
    } catch (err) {
      console.warn('Initial video status check deferred.');
    }
  };

  useEffect(() => {
    syncStatus();
    const interval = setInterval(syncStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  // WebSocket real-time subscription
  useEffect(() => {
    telemetryWS.connect();
    const unsubscribe = telemetryWS.subscribe((data) => {
      setTelemetry(data);
      if (data.traffic_light_state) {
        setTrafficLightState(data.traffic_light_state);
      }
    });
    return () => unsubscribe();
  }, []);

  const handleStartProcessing = async (options = { source_type: 'demo' }) => {
    try {
      const status = await TrafficService.startVideo(options);
      setVideoStatus(status);
    } catch (err) {
      console.error('Failed to start processing:', err);
    }
  };

  const handleStopProcessing = async () => {
    try {
      const status = await TrafficService.stopVideo();
      setVideoStatus(status);
    } catch (err) {
      console.error('Failed to stop processing:', err);
    }
  };

  const handlePauseProcessing = async () => {
    try {
      const status = await TrafficService.pauseVideo();
      setVideoStatus(status);
    } catch (err) {
      console.error('Failed to pause processing:', err);
    }
  };

  const handleResumeProcessing = async () => {
    try {
      const status = await TrafficService.resumeVideo();
      setVideoStatus(status);
    } catch (err) {
      console.error('Failed to resume processing:', err);
    }
  };

  const handleTrafficLightChange = async (newState) => {
    try {
      await TrafficService.setTrafficLight(newState);
      setTrafficLightState(newState);
    } catch (err) {
      console.error('Failed to set traffic light:', err);
    }
  };

  const isStreaming = videoStatus?.status === 'PROCESSING';

  return (
    <div className="flex min-h-screen bg-background text-slate-100 font-sans">
      {/* Navigation Sidebar */}
      <Sidebar
        isStreaming={isStreaming}
        activeViolationsCount={telemetry?.new_violations?.length || 0}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-x-hidden">
        <Navbar
          trafficLightState={trafficLightState}
          onTrafficLightChange={handleTrafficLightChange}
          videoStatus={videoStatus}
          onStartDemo={() => handleStartProcessing({ source_type: 'demo' })}
          onStopProcessing={handleStopProcessing}
        />

        <main className="flex-1 p-8 max-w-7xl w-full mx-auto">
          <Routes>
            <Route
              path="/"
              element={
                <DashboardPage
                  telemetry={telemetry}
                  trafficLightState={trafficLightState}
                  onTrafficLightChange={handleTrafficLightChange}
                />
              }
            />
            <Route
              path="/live"
              element={
                <LiveMonitoringPage
                  videoStatus={videoStatus}
                  telemetry={telemetry}
                  trafficLightState={trafficLightState}
                  onTrafficLightChange={handleTrafficLightChange}
                  onStartProcessing={handleStartProcessing}
                  onStopProcessing={handleStopProcessing}
                  onPauseProcessing={handlePauseProcessing}
                  onResumeProcessing={handleResumeProcessing}
                />
              }
            />
            <Route path="/violations" element={<ViolationsPage />} />
            <Route path="/vehicles" element={<VehiclesPage />} />
            <Route path="/vehicles/:id" element={<VehicleDetailsPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}
