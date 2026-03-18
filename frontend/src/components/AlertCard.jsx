import React from 'react';

const AlertCard = ({ title, location, time, severity, onClick }) => {
  const severityConfig = {
    HIGH: { 
      bg: 'bg-red-500', 
      text: 'text-white', 
      border: 'border-red-500',
      icon: (
        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      )
    },
    MEDIUM: { 
      bg: 'bg-yellow-400', 
      text: 'text-gray-900', 
      border: 'border-yellow-400',
      icon: (
        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      )
    },
    LOW: { 
      bg: 'bg-blue-400', 
      text: 'text-white', 
      border: 'border-blue-400',
      icon: (
        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )
    }
  };

  const currentSeverity = severityConfig[severity] || severityConfig.LOW;

  return (
    <div 
      className={`bg-gray-800 rounded-xl p-4 mb-3 transition-all cursor-pointer border-l-4 ${currentSeverity.border} shadow-lg hover:shadow-xl hover:bg-gray-700 transform hover:-translate-y-0.5`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-3">
        <h4 className="text-sm font-bold text-white">{title}</h4>
        <span 
          className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold ${currentSeverity.bg} ${currentSeverity.text} shadow-sm`}
        >
          {currentSeverity.icon}
          {severity}
        </span>
      </div>
      <div className="flex items-center text-xs text-gray-300 mb-1">
        <svg className="w-3.5 h-3.5 mr-1.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        {location}
      </div>
      <div className="flex items-center text-xs text-gray-400">
        <svg className="w-3.5 h-3.5 mr-1.5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        {time}
      </div>
    </div>
  );
};

export default AlertCard;




