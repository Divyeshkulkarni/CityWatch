import React, { useState } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import CameraFeed from './components/CameraFeed';
import AnalyticsBar from './components/AnalyticsBar';
import PieChart from './components/PieChart';
import ReportModal from './components/ReportModal';
import HomeDashboard from './components/HomeDashboard';
import TempleDashboard from './components/TempleDashboard';
import StationManagement from './components/StationManagement';
import { FiTrendingUp } from 'react-icons/fi';
import highwayLogo from '../logo/highway.png';

function App() {
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState('home'); // 'home' | 'dashboard' | 'temple' | 'station'
  const [activeArea, setActiveArea] = useState('(All Areas)');

  const allCameras = [
    { id: 'CAM-01', location: 'Entrance Main', hasAlert: false },
    { id: 'CAM-02', location: 'Toll Plaza East', hasAlert: true },
    { id: 'CAM-03', location: 'Approach A1', hasAlert: false },
    { id: 'CAM-04', location: 'Highway Entry Merge', hasAlert: false },
  ];

  const cameras = activeArea === '(All Areas)' 
    ? allCameras 
    : [allCameras.find(c => c.location.toLowerCase().includes(activeArea.toLowerCase().replace('lanes', 'approach'))) || allCameras[0]];

  const handleAlertClick = (alert) => {
    setSelectedAlert(alert);
    setIsReportModalOpen(true);
  };

  const handleGenerateReport = () => {
    // If an alert is already selected, open modal with that alert
    // Otherwise, use a default alert for demonstration
    if (selectedAlert) {
      setIsReportModalOpen(true);
    } else {
      // Default alert for demonstration when button is clicked directly
      setSelectedAlert({
        title: 'Traffic Analysis Report',
        location: 'Highway Monitoring System',
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

  if (currentPage === 'home') {
    return (
      <HomeDashboard 
        onNavigateToDashboard={() => setCurrentPage('dashboard')} 
        onNavigateToTemple={() => setCurrentPage('temple')} 
        onNavigateToStation={() => setCurrentPage('station')}
      />
    );
  }

  if (currentPage === 'temple') {
    return (
      <TempleDashboard 
        onNavigateToHome={() => setCurrentPage('home')}
        onNavigateToDashboard={() => setCurrentPage('dashboard')}
        onNavigateToStation={() => setCurrentPage('station')}
      />
    );
  }

  if (currentPage === 'station') {
    return (
      <StationManagement 
        onNavigateToHome={() => setCurrentPage('home')}
        onNavigateToDashboard={() => setCurrentPage('dashboard')} 
        onNavigateToTemple={() => setCurrentPage('temple')} 
      />
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <Header onGenerateReport={handleGenerateReport} onNavigateToHome={() => setCurrentPage('home')} bgColor="#6EC639" logo={highwayLogo} />
      <Sidebar 
        onAlertClick={handleAlertClick} 
        onNavigateToHome={() => setCurrentPage('home')}
        onNavigateToDashboard={() => setCurrentPage('dashboard')}
        onNavigateToTemple={() => setCurrentPage('temple')}
        onNavigateToStation={() => setCurrentPage('station')}
        themeColor="#6EC639"
        activeArea={activeArea}
        setActiveArea={setActiveArea}
      />

      {/* Main Content Area */}
      <main className="ml-80 pt-16 p-6 bg-white">
        {/* CCTV Camera Grid Container - Bento Box Style */}
        <div className={`glassmorphism rounded-xl p-4 mb-6 mt-3 border border-white border-opacity-10 shadow-xl ${cameras.length === 1 ? 'max-w-3xl mx-auto' : 'w-full'}`}>
          <div className="flex items-center justify-between mb-4 px-2">
            <h2 className="text-xs font-bold text-white uppercase tracking-widest flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
              LIVE CAMERA - {activeArea}
            </h2>
            <span className="text-[10px] text-white/50 font-medium">1080p Stream</span>
          </div>
          <div className={`grid ${cameras.length > 1 ? 'grid-cols-2' : 'grid-cols-1'} gap-4`}>
            {cameras.map((camera) => (
              <CameraFeed key={camera.id} {...camera} />
            ))}
          </div>
        </div>

        {/* Traffic Analytics Section */}
        <div className="backdrop-blur-md border border-white/10 rounded-2xl p-6 mb-6 bg-custom-green">
          <div className="flex flex-col lg:flex-row gap-8">
            {/* Left Side - Analytics Bars (70%) */}
            <div className="flex-[0.7]">
              <h2 className="text-lg font-bold text-white uppercase tracking-wider mb-6 flex items-center gap-2">
                <FiTrendingUp className="text-white" />
                TRAFFIC ANALYTICS
              </h2>
              <div className="space-y-6">
                <div className="p-4 bg-white/10 border border-white/20 rounded-xl">
                  <AnalyticsBar
                    label="Vehicle Count"
                    value={1247}
                    unit="vehicles/hr"
                    percentage={78}
                  />
                </div>
                <div className="p-4 bg-white/10 border border-white/20 rounded-xl">
                  <AnalyticsBar
                    label="Average Speed"
                    value={65}
                    unit="MPH"
                    percentage={85}
                  />
                </div>
                <div className="p-4 bg-white/10 border border-white/20 rounded-xl">
                  <AnalyticsBar
                    label="Traffic Flow Efficiency"
                    value={92}
                    unit="%"
                    percentage={92}
                  />
                </div>
              </div>
            </div>

            {/* Right Side - Donut Chart (30%) */}
            <div className="flex-[0.3] flex items-center justify-center p-4 bg-white/10 border border-white/20 rounded-xl relative overflow-hidden">
              <div className="absolute bottom-0 right-0 w-40 h-40 bg-white/10 rounded-full blur-3xl"></div>
              <div className="w-full relative z-10">
                <PieChart
                  title="VEHICLE TYPE DISTRIBUTION"
                  showCenterLabel={true}
                  data={[
                    { name: 'Cars', value: 44, color: '#3b82f6' },
                    { name: 'Trucks', value: 35, color: '#6EC639' },
                    { name: 'Buses', value: 10, color: '#f59e0b' },
                    { name: 'Motorcycles', value: 5, color: '#8b5cf6' },
                    { name: 'Other', value: 6, color: '#ef4444' },
                  ]}
                  colors={['#3b82f6', '#6EC639', '#f59e0b', '#8b5cf6', '#ef4444']}
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
}

export default App;



