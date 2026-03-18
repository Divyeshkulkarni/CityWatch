import React, { useState } from 'react';
import Header from './Header';
import Sidebar from './Sidebar';
import CameraFeed from './CameraFeed';
import AnalyticsBar from './AnalyticsBar';
import PieChart from './PieChart';
import ReportModal from './ReportModal';
import { FiTrendingUp } from 'react-icons/fi';
import templeLogo from '../../logo/temple.png';

const TempleDashboard = ({ onNavigateToHome, onNavigateToDashboard, onNavigateToStation }) => {
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);
  const [activeArea, setActiveArea] = useState('(All Areas)');

  // Temple-specific camera feeds
  const allTempleCameras = [
    { id: 'TCM-01', location: 'Main Entrance Gate', hasAlert: false },
    { id: 'TCM-02', location: 'Inner Sanctum', hasAlert: true },
    { id: 'TCM-03', location: 'Queue Area A', hasAlert: false },
    { id: 'TCM-04', location: 'Parking Complex', hasAlert: false },
  ];

  const templeCameras = activeArea === '(All Areas)'
    ? allTempleCameras
    : [allTempleCameras.find(c => c.location.toLowerCase().includes(activeArea.toLowerCase().replace('lanes', 'queue').replace('flyover', 'sanctum').replace('bridge', 'parking'))) || allTempleCameras[0]];

  const handleAlertClick = (alert) => {
    setSelectedAlert(alert);
    setIsReportModalOpen(true);
  };

  const handleGenerateReport = () => {
    if (selectedAlert) {
      setIsReportModalOpen(true);
    } else {
      setSelectedAlert({
        title: 'Temple Crowd Analysis Report',
        location: 'Temple Monitoring System',
        time: new Date().toLocaleTimeString(),
        severity: 'MEDIUM',
      });
      setIsReportModalOpen(true);
    }
  };

  const handleCloseModal = () => {
    setIsReportModalOpen(false);
    setSelectedAlert(null);
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Custom Temple Header */}
      <header className="fixed top-0 left-0 right-0 z-50 h-16 shadow-lg" style={{ backgroundColor: '#FFC300', backdropFilter: 'blur(10px)' }}>
        <div className="flex items-center justify-between h-full px-6">
          {/* Left Side */}
          <div className="flex items-center gap-4">
            <span className="text-lg font-semibold text-white">Temple Management</span>
            <span className="px-3 py-1 bg-red-500 text-white text-xs font-bold rounded-full">
              LIVE SYSTEM
            </span>
          </div>

          {/* Center Title */}
          <div className="absolute left-1/2 transform -translate-x-1/2 flex items-center gap-3">
            <div className="w-8 h-8 flex items-center justify-center">
              <img src={templeLogo} alt="Temple Logo" className="w-full h-full object-contain" />
            </div>
            <h1 className="text-2xl font-bold text-white tracking-wider">TEMPLE CROWD MANAGEMENT</h1>
          </div>

          <div className="flex items-center gap-3">

            <button
              onClick={() => {
                if (!document.fullscreenElement) {
                  document.documentElement.requestFullscreen();
                } else if (document.exitFullscreen) {
                  document.exitFullscreen();
                }
              }}
              className="w-10 h-10 flex items-center justify-center bg-white/10 hover:bg-white/20 text-white rounded-lg transition-all shadow-md active:scale-95"
              title="Toggle Fullscreen"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            </button>
            <button
              onClick={handleGenerateReport}
              className="px-4 py-2 text-gray-800 rounded-lg font-semibold shadow-md"
              style={{ backgroundColor: 'white' }}
            >
              GENERATE REPORT
            </button>
            <button
              onClick={onNavigateToHome}
              className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-orange-600 transition-colors"
            >
              <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
              </svg>
            </button>
          </div>
        </div>
      </header>
      <Sidebar
        onAlertClick={handleAlertClick}
        onNavigateToHome={onNavigateToHome}
        onNavigateToDashboard={onNavigateToDashboard}
        onNavigateToTemple={() => { }}
        onNavigateToStation={onNavigateToStation}
        themeColor="#FFC300"
        activeArea={activeArea}
        setActiveArea={setActiveArea}
      />

      {/* Main Content Area */}
      <main className="ml-80 pt-16 p-6 bg-white">
        {/* CCTV Camera Grid Container - Temple Monitoring */}
        <div className={`glassmorphism rounded-xl p-4 mb-6 mt-3 border border-white border-opacity-10 shadow-xl ${templeCameras.length === 1 ? 'max-w-3xl mx-auto' : 'w-full'}`} style={{ backgroundColor: 'rgba(255, 168, 47, 1)' }}>
          <div className="flex items-center justify-between mb-4 px-2">
            <h2 className="text-xs font-bold text-white uppercase tracking-widest flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-red-600 animate-pulse"></span>
              LIVE CAMERA - {activeArea}
            </h2>
            <span className="text-[10px] text-white/50 font-medium">1080p Secure Stream</span>
          </div>
          <div className={`grid ${templeCameras.length > 1 ? 'grid-cols-2' : 'grid-cols-1'} gap-4`}>
            {templeCameras.map((camera) => (
              <CameraFeed key={camera.id} {...camera} />
            ))}
          </div>
        </div>

        {/* Temple Crowd Analytics Section */}
        <div className="backdrop-blur-md border border-white/10 rounded-2xl p-6 mb-6" style={{ backgroundColor: '#FFA82F' }}>
          <div className="flex flex-col lg:flex-row gap-8">
            {/* Left Side - Analytics Bars (70%) */}
            <div className="flex-[0.7]">
              <h2 className="text-lg font-bold text-white uppercase tracking-wider mb-6 flex items-center gap-2">
                <FiTrendingUp className="text-white" />
                CROWD ANALYTICS
              </h2>
              <div className="space-y-6">
                <div className="p-4 bg-white/10 border border-white/20 rounded-xl">
                  <AnalyticsBar
                    label="Current Occupancy"
                    value={847}
                    unit="devotees"
                    percentage={72}
                  />
                </div>
                <div className="p-4 bg-white/10 border border-white/20 rounded-xl">
                  <AnalyticsBar
                    label="Queue Wait Time"
                    value={25}
                    unit="minutes"
                    percentage={45}
                  />
                </div>
                <div className="p-4 bg-white/10 border border-white/20 rounded-xl">
                  <AnalyticsBar
                    label="Safety Compliance"
                    value={94}
                    unit="%"
                    percentage={94}
                  />
                </div>
              </div>
            </div>

            {/* Right Side - Donut Chart (30%) */}
            <div className="flex-[0.3] flex items-center justify-center p-4 bg-white/10 border border-white/20 rounded-xl relative overflow-hidden">
              <div className="absolute bottom-0 right-0 w-40 h-40 bg-white/10 rounded-full blur-3xl"></div>
              <div className="w-full relative z-10">
                <PieChart
                  title="DEVOTEE DISTRIBUTION"
                  showCenterLabel={true}
                  data={[
                    { name: 'Regular', value: 35, color: '#3b82f6' },
                    { name: 'First-Time', value: 25, color: '#10b981' },
                    { name: 'VIP', value: 15, color: '#f59e0b' },
                    { name: 'Elderly', value: 20, color: '#8b5cf6' },
                    { name: 'Children', value: 5, color: '#ef4444' },
                  ]}
                  colors={['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444']}
                />
              </div>
            </div>
          </div>
        </div>


      </main>

      {/* Report Modal */}
      {isReportModalOpen && (
        <ReportModal alert={selectedAlert} onClose={handleCloseModal} />
      )}
    </div>
  );
};

export default TempleDashboard;
