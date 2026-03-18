import React from 'react';

const Header = ({ onGenerateReport, onNavigateToHome, title = "HIGHWAY MONITORING", bgColor = 'rgba(62, 64, 149, 1)', logo }) => {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 h-16 shadow-lg" style={{ backgroundColor: bgColor, backdropFilter: 'blur(10px)' }}>
      <div className="flex items-center justify-between h-full px-6">
        {/* Left Side */}
        <div className="flex items-center gap-4">
          <span className="text-lg font-semibold text-white">Dashboard</span>
          <span className="px-3 py-1 bg-red-500 text-white text-xs font-bold rounded-full">
            LIVE SYSTEM
          </span>
        </div>

        {/* Center Title */}
        <div className="absolute left-1/2 transform -translate-x-1/2 flex items-center gap-3">
          {logo && (
            <div className="w-8 h-8 flex items-center justify-center">
              <img src={logo} alt="Header Logo" className="w-full h-full object-contain" />
            </div>
          )}
          <h1 className="text-2xl font-bold text-white tracking-wider uppercase">{title}</h1>
        </div>

        {/* Right Side - Full Screen, Generate Report Button and Close Button */}
        <div className="flex items-center gap-3">
          <button 
            onClick={() => {
              if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen();
              } else {
                if (document.exitFullscreen) {
                  document.exitFullscreen();
                }
              }
            }}
            className="w-10 h-10 flex items-center justify-center bg-white/10 hover:bg-white/20 text-white rounded-lg transition-all shadow-md"
            title="Toggle Fullscreen"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
            </svg>
          </button>
          <button 
            onClick={onGenerateReport}
            className="px-4 py-2 bg-white text-gray-800 rounded-lg hover:bg-gray-100 transition-all font-semibold shadow-md"
          >
            GENERATE REPORT
          </button>
          <button onClick={onNavigateToHome} className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-700 transition-colors">
            <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
            </svg>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;

