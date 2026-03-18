import React, { useState } from 'react';
import Header from './Header';
import CameraFeed from './CameraFeed';
import AnalyticsBar from './AnalyticsBar';
import PieChart from './PieChart';
import ReportModal from './ReportModal';
import { FiHome, FiMapPin, FiActivity, FiAlertTriangle, FiUsers, FiClock, FiVideo, FiTrendingUp } from 'react-icons/fi';
import stationLogo from '../../logo/station.png';

// A specialized Sidebar for the Station Management page to fit the dark theme
const StationSidebar = ({ activeArea, setActiveArea, onAlertClick, onNavigateToHome, onNavigateToDashboard, onNavigateToTemple }) => {
  const areas = ['Platform', 'Stairs', 'Bridge', 'Runway', 'Entrance'];

  const alerts = [
    { title: 'High Congestion', location: 'Platform 3', time: '2 min ago', severity: 'HIGH' },
    { title: 'Unusual Object', location: 'Runway Approach', time: '5 min ago', severity: 'MEDIUM' },
    { title: 'Crowd Pooling', location: 'Main Entrance', time: '8 min ago', severity: 'LOW' },
  ];

  return (
    <aside className="fixed left-0 top-16 bottom-0 w-80 bg-white border-r border-gray-200 overflow-y-auto scrollbar-hide z-40">
      <div className="p-5 flex flex-col h-full">
        {/* Area Division Section */}
        <div className="mb-8 flex-1">
          <h2 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-4">AREA DIVISION</h2>
          <div className="space-y-2">
            {areas.map((area) => (
              <button
                key={area}
                onClick={() => setActiveArea(area)}
                className={`w-full text-left px-5 py-2.5 rounded-lg transition-all font-medium border ${
                  activeArea === area
                    ? 'text-white border-transparent shadow-[0_4px_10px_rgba(62,64,149,0.3)]'
                    : 'bg-transparent border-transparent text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                }`}
                style={activeArea === area ? { backgroundColor: 'rgba(62, 64, 149, 1)' } : {}}
              >
                {area}
              </button>
            ))}
          </div>
        </div>

        {/* Recent Alerts Section */}
        <div className="mb-6 mt-auto">
          <h2 className="text-xs font-bold text-rose-500 uppercase tracking-wider mb-4 flex items-center gap-2">
            <FiAlertTriangle /> RECENT ALERTS
          </h2>
          <div className="space-y-3">
            {alerts.slice(0, 2).map((alert, index) => (
              <div 
                key={index}
                onClick={() => onAlertClick && onAlertClick(alert)} 
                className={`p-3 rounded-xl border cursor-pointer hover:-translate-y-0.5 transition-all ${
                  alert.severity === 'HIGH' ? 'bg-rose-50 border-rose-200 text-rose-800' : 
                  'bg-amber-50 border-amber-200 text-amber-800'
                }`}
              >
                <div className="flex justify-between items-start mb-1">
                  <span className="font-bold text-sm tracking-wide">{alert.title}</span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded uppercase font-bold ${
                    alert.severity === 'HIGH' ? 'bg-rose-500 text-white' : 'bg-amber-500 text-white'
                  }`}>{alert.severity}</span>
                </div>
                <div className="flex justify-between items-center text-xs opacity-70">
                  <span>{alert.location}</span>
                  <span>{alert.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Preview All Alerts Button */}
        <button 
          className="w-full py-2.5 px-4 text-white rounded-lg hover:opacity-90 transition-all font-bold shadow-lg uppercase tracking-wider text-sm mt-4" 
          style={{ backgroundColor: 'rgba(62, 64, 149, 1)' }}
        >
          PREVIEW ALL ALERTS
        </button>
      </div>
    </aside>
  );
};

const StationManagement = ({ onNavigateToHome, onNavigateToDashboard, onNavigateToTemple }) => {
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);
  const [activeArea, setActiveArea] = useState('Platform');

  const getCamerasForArea = (area) => {
    switch(area) {
       case 'Platform': return [
         { id: 'STN-CAM-01', location: 'Platform 1 North', hasAlert: true },
         { id: 'STN-CAM-02', location: 'Platform 2 South', hasAlert: false },
         { id: 'STN-CAM-11', location: 'Platform 3 East', hasAlert: false },
         { id: 'STN-CAM-12', location: 'Platform 4 West', hasAlert: false },
       ];
       case 'Stairs': return [
         { id: 'STN-CAM-03', location: 'Escalator B', hasAlert: false },
         { id: 'STN-CAM-04', location: 'Stairway 4 Main', hasAlert: true },
       ];
       case 'Bridge': return [
         { id: 'STN-CAM-05', location: 'Overbridge East', hasAlert: false },
         { id: 'STN-CAM-06', location: 'Overbridge West', hasAlert: false },
       ];
       case 'Runway': return [
         { id: 'STN-CAM-07', location: 'Track 1 Approach', hasAlert: false },
         { id: 'STN-CAM-08', location: 'Track 2 Merge', hasAlert: false },
       ];
       case 'Entrance': return [
         { id: 'STN-CAM-09', location: 'Main Turnstiles', hasAlert: true },
         { id: 'STN-CAM-10', location: 'Ticketing Hall', hasAlert: false },
       ];
       default: return [];
    }
  };

  const cameras = getCamerasForArea(activeArea);

  // Mock data specific to a train station
  const stationCrowdData = [
    { name: 'Platform 1', value: 35, color: '#3b82f6' },
    { name: 'Platform 2', value: 15, color: '#10b981' },
    { name: 'Main Concourse', value: 40, color: '#f59e0b' },
    { name: 'Ticketing Area', value: 10, color: '#8b5cf6' }
  ];

  const handleAlertClick = (alert) => {
    setSelectedAlert(alert);
    setIsReportModalOpen(true);
  };

  const handleGenerateReport = () => {
    if (selectedAlert) {
      setIsReportModalOpen(true);
    } else {
      setSelectedAlert({
        title: 'Station Congestion Report',
        location: `Station Monitoring - ${activeArea}`,
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
    <div className="min-h-screen bg-white font-sans text-slate-200 selection:bg-blue-500/30">
      
      {/* We reuse the Header but it expects onGenerateReport */}
      <Header onGenerateReport={handleGenerateReport} onNavigateToHome={onNavigateToHome} title="STATION CROWD MANAGEMENT" logo={stationLogo} />

      {/* Custom Station Sidebar */}
      <StationSidebar 
         activeArea={activeArea} 
         setActiveArea={setActiveArea} 
         onAlertClick={handleAlertClick} 
         onNavigateToHome={onNavigateToHome}
         onNavigateToDashboard={onNavigateToDashboard}
         onNavigateToTemple={onNavigateToTemple}
      />

      {/* Main Content Area mirroring App.jsx structure but customized for dark theme */}
      <main className="ml-80 pt-20 p-6 relative">
        <div className="absolute -top-10 -left-10 w-40 h-40 bg-blue-500/10 rounded-full blur-3xl pointer-events-none"></div>

        {/* Header Title Layer */}

        {/* CCTV Camera Grid Container - Bento Box Style */}
        <div className="backdrop-blur-md rounded-2xl p-4 mb-6 border border-white/10 shadow-xl overflow-hidden relative" style={{ backgroundColor: 'rgba(62, 64, 149, 1)' }}>
          <div className="absolute top-0 right-0 w-64 h-64 bg-rose-500/5 rounded-full blur-3xl"></div>
          
          <div className="flex justify-between items-center mb-4 relative z-10 px-2">
            <h2 className="text-sm font-bold uppercase tracking-wider flex items-center gap-2 text-white">
              <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></span>
              LIVE CAMERAS - {activeArea}
            </h2>
            <span className="bg-white/10 border border-white/20 text-xs px-2 py-1 rounded text-white">
              {cameras.length} Active Feeds
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 relative z-10">
            {cameras.map((camera) => (
              <CameraFeed key={camera.id} {...camera} />
            ))}
          </div>
        </div>

        {/* Traffic Analytics Section */}
        <div className="backdrop-blur-md border border-white/10 rounded-2xl p-6 mb-6" style={{ backgroundColor: 'rgba(62, 64, 149, 1)' }}>
          <div className="flex flex-col lg:flex-row gap-8">
            {/* Left Side - Analytics Bars (70%) */}
            <div className="flex-[0.7]">
              <h2 className="text-lg font-bold text-white uppercase tracking-wider mb-6 flex items-center gap-2">
                <FiTrendingUp className="text-blue-400" />
                CONCOURSE ANALYTICS
              </h2>
              <div className="space-y-6">
                <div className="p-4 bg-white/5 border border-white/5 rounded-xl">
                  <AnalyticsBar
                    label="Current Density"
                    value={4285}
                    unit="PAX/hr"
                    percentage={85}
                  />
                </div>
                <div className="p-4 bg-white/5 border border-white/5 rounded-xl">
                  <AnalyticsBar
                    label="Average Wait Time"
                    value={14}
                    unit="mins"
                    percentage={65}
                  />
                </div>
                <div className="p-4 bg-white/5 border border-white/5 rounded-xl">
                  <AnalyticsBar
                    label="Throughput Efficiency"
                    value={94}
                    unit="%"
                    percentage={94}
                  />
                </div>
              </div>
            </div>

            {/* Right Side - Donut Chart (30%) */}
            <div className="flex-[0.3] flex items-center justify-center p-4 bg-white/5 border border-white/5 rounded-xl relative overflow-hidden">
              <div className="absolute bottom-0 right-0 w-40 h-40 bg-blue-500/10 rounded-full blur-3xl"></div>
              <div className="w-full relative z-10">
                <PieChart
                  title="DENSITY DISTRIBUTION"
                  showCenterLabel={true}
                  data={stationCrowdData}
                  colors={stationCrowdData.map(d => d.color)}
                />
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Report Modal */}
      {isReportModalOpen && (
         <div className="fixed inset-0 z-50">
            <ReportModal alert={selectedAlert} onClose={handleCloseModal} />
         </div>
      )}
    </div>
  );
}

export default StationManagement;
