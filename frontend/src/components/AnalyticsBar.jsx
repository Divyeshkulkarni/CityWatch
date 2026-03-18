import React from 'react';

const AnalyticsBar = ({ label, value, unit, percentage, color = 'electric-blue' }) => {
  return (
    <div className="mb-5">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-semibold text-white">{label}</span>
        <span className="text-sm font-bold text-white">{value} {unit}</span>
      </div>
      <div className="h-3 bg-gray-100 rounded-full overflow-hidden relative border border-white/20">
        <div
          className="h-full rounded-full transition-all duration-1000 ease-out flex items-center justify-end pr-3 border border-black box-border"
          style={{ 
            width: `${percentage}%`,
            background: 'linear-gradient(90deg, #3967B3 0%, #d9b233ff 50%, #AC4241 100%)',
            border: '1px solid #00000066'
          }}
        >
          <span className="text-xs font-bold text-black">{percentage}%</span>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsBar;




