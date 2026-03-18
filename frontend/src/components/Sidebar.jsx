import React, { useState } from 'react';
import AlertCard from './AlertCard';

const Sidebar = ({ onAlertClick, themeColor = '#6EC639', activeArea, setActiveArea }) => {
  const areas = ['(All Areas)', 'Entrance', 'Flyover', 'Bridge', 'Lanes'];

  const alerts = [
    { title: 'High Congestion', location: 'Entrance Main', time: '2 min ago', severity: 'HIGH' },
    { title: 'Speed Violation', location: 'Toll Plaza East', time: '5 min ago', severity: 'MEDIUM' },
    { title: 'Weather Alert', location: 'Bridge Section', time: '8 min ago', severity: 'LOW' },
  ];

  return (
    <aside className="fixed left-0 top-16 bottom-0 w-80 bg-white border-r border-gray-200 overflow-y-auto scrollbar-hide">
      <div className="p-5">
        {/* Area Division Section */}
        <div className="mb-8">
          <h2 className="text-sm font-bold text-gray-700 uppercase tracking-wider mb-4">AREA DIVISION</h2>
          <div className="space-y-2">
            {areas.map((area) => (
              <button
                key={area}
                onClick={() => setActiveArea(area)}
                className={`w-full text-left px-5 py-2.5 rounded-lg transition-all font-medium ${
                  activeArea === area
                    ? 'text-white shadow-md'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
                }`}
                style={activeArea === area ? { backgroundColor: themeColor } : {}}
              >
                {area}
              </button>
            ))}
          </div>
        </div>

        {/* Recent Alerts Section */}
        <div className="mb-6">
          <h2 className="text-sm font-bold text-gray-700 uppercase tracking-wider mb-4">RECENT ALERTS</h2>
          <div>
            {alerts.map((alert, index) => (
              <AlertCard 
                key={index} 
                {...alert} 
                onClick={() => onAlertClick && onAlertClick(alert)}
              />
            ))}
          </div>
        </div>

        {/* Preview All Alerts Button */}
        <button 
          className="w-full py-2.5 px-4 text-white rounded-lg hover:opacity-90 transition-all font-semibold shadow-md"
          style={{ backgroundColor: themeColor }}
        >
          PREVIEW ALL ALERTS
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;




