import React, { useState, useEffect, useRef } from 'react';

const CameraFeed = ({ id, location, hasAlert = false }) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(document.fullscreenElement === containerRef.current);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  const toggleFullscreen = () => {
    if (!isFullscreen) {
      if (containerRef.current.requestFullscreen) {
        containerRef.current.requestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
  };

  return (
    <div 
      ref={containerRef}
      className={`relative rounded-xl overflow-hidden bg-[#6EC639] shadow-lg transition-all duration-300 ${
        isFullscreen ? 'w-full h-full rounded-none' : 'hover:scale-[1.02]'
      } ${
        hasAlert ? 'border-2 border-red-500 ring-2 ring-red-500 ring-opacity-50' : 'border border-white border-opacity-10'
      }`}
    >
      {/* Camera Feed Placeholder */}
      <div className={`${isFullscreen ? 'h-full w-full' : 'aspect-video'} bg-gray-800 relative flex items-center justify-center`}>
        {/* Placeholder image effect - simplified texture */}
        <div className="absolute inset-0 opacity-30">
          <div className="absolute inset-0" style={{
            backgroundImage: `
              repeating-linear-gradient(0deg, rgba(0,0,0,0.1) 0px, transparent 1px, transparent 2px, rgba(0,0,0,0.1) 3px),
              repeating-linear-gradient(90deg, rgba(255,255,255,0.02) 0px, transparent 1px, transparent 2px, rgba(255,255,255,0.02) 3px)
            `,
          }}></div>
        </div>

        {/* LIVE Badge */}
        <div className="absolute top-4 left-4 flex items-center gap-2 px-3 py-1.5 bg-red-500 rounded-lg text-sm font-bold text-white z-20">
          <span className="w-2.5 h-2.5 bg-white rounded-full animate-pulse"></span>
          LIVE
        </div>

        {/* REC Indicator */}
        <div className="absolute top-4 right-4 flex items-center gap-2 px-3 py-1.5 bg-black bg-opacity-70 rounded-lg text-sm font-semibold text-red-500 z-20">
          <span className="w-2.5 h-2.5 bg-red-500 rounded-full animate-pulse"></span>
          REC
        </div>

        {/* Alert Overlay - Red only for alerts */}
        {hasAlert && (
          <div className="absolute inset-0 bg-red-500 bg-opacity-20 flex items-center justify-center z-10">
            <div className="text-center">
              <svg className={`${isFullscreen ? 'w-20 h-20' : 'w-10 h-10'} text-red-500 mx-auto mb-4`} fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <p className={`${isFullscreen ? 'text-4xl' : 'text-base'} text-red-500 font-black tracking-widest`}>DETECTION ALERT</p>
            </div>
          </div>
        )}

        {/* Camera Info Overlay - Simplified */}
        <div className={`absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black via-black/80 to-transparent ${isFullscreen ? 'p-8' : 'p-4'} flex justify-between items-end z-20`}>
          <div>
            <p className={`${isFullscreen ? 'text-sm' : 'text-[10px]'} font-bold text-gray-400 uppercase tracking-[0.2em] mb-1`}>{id}</p>
            <p className={`${isFullscreen ? 'text-2xl' : 'text-sm'} font-bold text-white uppercase tracking-wider`}>
              LIVE CAMERA - {location}
            </p>
          </div>
          <button 
            onClick={(e) => {
              e.stopPropagation();
              toggleFullscreen();
            }}
            className={`${isFullscreen ? 'p-3' : 'p-2'} bg-white/10 hover:bg-white/20 rounded-xl text-white transition-all transform hover:scale-110 active:scale-95`}
            title={isFullscreen ? "Exit Full Screen" : "Full Screen Feed"}
          >
            {isFullscreen ? (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CameraFeed;


