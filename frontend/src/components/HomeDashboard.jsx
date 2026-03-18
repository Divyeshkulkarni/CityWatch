import React, { useState } from 'react';
import { FiMenu, FiBell, FiActivity, FiMapPin, FiTruck, FiAlertTriangle, FiLayout, FiSettings, FiInfo, FiShield, FiLogOut, FiTrendingUp } from 'react-icons/fi';
import PieChart from './PieChart';
import templeLogo from '../../logo/temple.png';
import stationLogo from '../../logo/station.png';
import highwayLogo from '../../logo/highway.png';
import mainLogo from '../../logo/logo.png';

const HomeDashboard = ({ onNavigateToDashboard, onNavigateToTemple, onNavigateToStation }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [activeModal, setActiveModal] = useState(null); // 'settings' | 'about' | 'privacy' | 'notifications' | null

  const mockChartData = [
    { name: 'Temple Area', value: 45, color: '#f59e0b' },
    { name: 'Station Crowd', value: 30, color: '#3b82f6' },
    { name: 'Highway Traffic', value: 25, color: '#6EC639' }
  ];

  return (
    <>
    <div className="min-h-screen bg-[#0f172a] bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-indigo-900/40 via-[#0f172a] to-slate-900 flex flex-col font-sans text-slate-200 selection:bg-purple-500/30">

      {/* Premium Glass Top Navigation */}
      <header className="sticky top-0 z-40 backdrop-blur-xl border-b border-white/10 shadow-2xl" style={{ backgroundColor: 'white' }}>
        <div className="w-full px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 -ml-2 mr-2 rounded-xl text-slate-800 hover:text-slate-900 hover:bg-black/5 transition-all duration-300 active:scale-95"
            >
              <FiMenu className="w-6 h-6" />
            </button>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center overflow-hidden">
                <img src={mainLogo} alt="Logo" className="w-full h-full object-contain" />
              </div>
              <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
                CROWD & TRAFFIC CONTROL
              </h1>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden md:flex items-center px-4 py-2 rounded-full bg-black/5 border border-black/10 text-sm font-medium text-slate-800">
              <span className="w-2 h-2 rounded-full bg-emerald-500 mr-2 animate-pulse"></span>
              System Online
            </div>
            <button 
              onClick={() => {
                if (!document.fullscreenElement) {
                  document.documentElement.requestFullscreen();
                } else if (document.exitFullscreen) {
                  document.exitFullscreen();
                }
              }}
              className="p-2 rounded-xl text-slate-800 hover:text-slate-900 hover:bg-black/5 transition-all duration-300 active:scale-95"
              title="Toggle Fullscreen"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            </button>
            <button 
              onClick={() => setActiveModal('notifications')}
              className="relative p-2 rounded-xl text-slate-800 hover:text-slate-900 hover:bg-black/5 transition-all duration-300 group"
            >
              <FiBell className="w-6 h-6 group-hover:rotate-12 transition-transform" />
              <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-pink-500 rounded-full border-2 border-white"></span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Layout */}
      <div className="flex flex-1 overflow-hidden relative">

        {/* Animated Sidebar */}
        <aside
          className={`${isSidebarOpen ? 'translate-x-0 w-72' : '-translate-x-full w-0'} transition-all duration-500 ease-in-out shrink-0 bg-slate-900/40 backdrop-blur-xl border-r border-white/10 flex flex-col z-30 absolute md:static h-full`}
        >
          <div className="flex-1 overflow-y-auto py-6 px-4 space-y-6">
            <div className="space-y-1">
              <p className="px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Core Modules</p>

              <button
                onClick={onNavigateToTemple}
                className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-white font-medium bg-[#f59e0b]/20 hover:bg-[#f59e0b]/30 transition-all duration-300 group"
              >
                <div className="p-1 rounded-lg bg-[#f59e0b]/30 transition-colors w-10 h-10 flex items-center justify-center overflow-hidden">
                  <img src={templeLogo} alt="Temple" className="w-full h-full object-contain" />
                </div>
                Temple Management
              </button>

              <button
                onClick={onNavigateToStation}
                className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-white font-medium bg-[#3b82f6]/20 hover:bg-[#3b82f6]/30 transition-all duration-300 group mt-2"
              >
                <div className="p-1 rounded-lg bg-[#3b82f6]/30 transition-colors w-10 h-10 flex items-center justify-center overflow-hidden">
                  <img src={stationLogo} alt="Station" className="w-full h-full object-contain" />
                </div>
                Station Management
              </button>

              <button
                onClick={onNavigateToDashboard}
                className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-[#6EC639] text-white font-medium border border-white/20 shadow-lg shadow-[#6EC639]/20 hover:bg-[#5db030] transition-all duration-300 group mt-2"
              >
                <div className="p-1 rounded-lg bg-white/20 transition-colors w-10 h-10 flex items-center justify-center overflow-hidden">
                  <img src={highwayLogo} alt="Highway" className="w-full h-full object-contain text-white" />
                </div>
                Highway Monitoring
              </button>
            </div>

            <div className="space-y-1 pt-4 border-t border-white/5">
              <p className="px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">System</p>

              {[
                { icon: FiSettings, label: 'Settings', id: 'settings' },
                { icon: FiInfo, label: 'About System', id: 'about' },
                { icon: FiShield, label: 'Privacy & Security', id: 'privacy' },
              ].map((item, i) => (
                <button 
                  key={i} 
                  onClick={() => setActiveModal(item.id)}
                  className="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-slate-400 font-medium hover:bg-white/5 hover:text-slate-200 transition-all duration-300"
                >
                  <item.icon className="w-4 h-4" />
                  {item.label}
                </button>
              ))}
            </div>
          </div>

          <div className="p-4 border-t border-white/10">
            <button className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-rose-500/10 text-rose-400 font-medium hover:bg-rose-500 hover:text-white transition-all duration-300">
              <FiLogOut className="w-4 h-4" />
              <span>Sign Out</span>
            </button>
          </div>
        </aside>

        {/* Backdrop for mobile sidebar */}
        {!isSidebarOpen && <div className="hidden" />}
        {isSidebarOpen && (
          <div
            className="md:hidden fixed inset-0 bg-slate-900/80 backdrop-blur-sm z-20"
            onClick={() => setIsSidebarOpen(false)}
          />
        )}

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto w-full">
          <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-8">

            {/* Header Section */}
            <div className="space-y-2 relative">
              <div className="absolute -top-10 -left-10 w-40 h-40 bg-purple-500/20 rounded-full blur-3xl pointer-events-none"></div>
              <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight relative z-10">
                Object Detection Models
              </h2>
              <p className="text-slate-400 max-w-2xl text-sm sm:text-base relative z-10">
                Real-time situational awareness powered by advanced machine learning.
                Monitoring movement across critical infrastructure hubs.
              </p>
            </div>

            {/* ODM Implementation Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                {
                  title: 'Temple Crowd Control',
                  icon: templeLogo,
                  cardBg: 'bg-[rgba(255,168,47,1)]',
                  onClick: onNavigateToTemple,
                  text: 'Real-time monitoring of entry/exit gates, queue density, and emergency routes to ensure safe movement during peak festivals.',
                },
                {
                  title: 'Station Congestion',
                  icon: stationLogo,
                  cardBg: 'bg-[#3E4095]',
                  onClick: onNavigateToStation,
                  text: 'Automated crowd flow analysis across platforms and ticketing zones to prevent bottlenecks and support incident response.',
                },
                {
                  title: 'Highway Surveillance',
                  icon: highwayLogo,
                  cardBg: 'bg-[#6EC639]',
                  onClick: onNavigateToDashboard,
                  text: 'Integrated surveillance of traffic lanes and toll plazas to detect congestion, stalled vehicles, and violations.',
                }
              ].map((card, i) => (
                <div
                  key={i}
                  onClick={card.onClick}
                  className={`group ${card.cardBg} backdrop-blur-md border border-white/20 rounded-2xl p-6 hover:shadow-2xl hover:-translate-y-1 transition-all duration-500 cursor-pointer overflow-hidden relative`}
                >
                  <div className="absolute -right-10 -top-10 w-32 h-32 bg-white/10 rounded-full blur-2xl group-hover:scale-150 transition-transform duration-700"></div>

                  <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-6 shadow-lg relative z-10 bg-white/20 p-2 overflow-hidden">
                    <img src={card.icon} alt={card.title} className="w-full h-full object-contain" />
                  </div>
                  <h3 className="text-lg font-bold text-white mb-3 relative z-10">{card.title}</h3>
                  <p className="text-sm text-white/90 leading-relaxed relative z-10">
                    {card.text}
                  </p>
                </div>
              ))}
            </div>



            {/* Bottom Panels Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 mb-12">

              {/* Live Alerts */}
              <div className="lg:col-span-2 backdrop-blur-md border border-white/10 rounded-3xl p-6 sm:p-8 flex flex-col relative overflow-hidden" style={{ backgroundColor: 'white' }}>
                <div className="absolute top-0 right-0 w-64 h-64 bg-rose-500/5 rounded-full blur-3xl"></div>

                <div className="flex items-center justify-between mb-6 relative z-10">
                  <h3 className="text-xl font-bold text-slate-900 flex items-center gap-3">
                    <FiAlertTriangle className="text-rose-400" />
                    Live Alerts
                  </h3>
                  <span className="flex h-3 w-3 relative">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-rose-500"></span>
                  </span>
                </div>

                <div className="space-y-4 flex-1 relative z-10">
                  {[
                    { text: 'High congestion detected near Temple North Gate.', time: 'Just now', type: 'critical' },
                    { text: 'Unusual crowd density at Central Station platform 3.', time: '2m ago', type: 'warning' },
                    { text: 'Slow-moving traffic on Highway Sector A1.', time: '15m ago', type: 'info' },
                  ].map((alert, i) => (
                    <div key={i} className="group relative bg-white/50 hover:bg-slate-50 border border-slate-200 rounded-2xl p-4 transition-colors">
                      <div className={`absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 rounded-r-md ${alert.type === 'critical' ? 'bg-rose-500' :
                        alert.type === 'warning' ? 'bg-amber-500' : 'bg-blue-500'
                        }`}></div>
                      <div className="pl-3">
                        <p className="text-sm text-slate-800 font-medium mb-1">{alert.text}</p>
                        <p className="text-xs text-slate-600">{alert.time}</p>
                      </div>
                    </div>
                  ))}
                </div>

                  <button 
                    onClick={() => setActiveModal('notifications')}
                    className="w-full mt-6 py-3 rounded-xl border border-slate-200 text-sm font-medium text-slate-700 hover:bg-slate-100 hover:text-slate-900 transition-colors relative z-10"
                  >
                    View All Notifications
                  </button>
              </div>

              {/* Analytics Summary */}
              <div className="lg:col-span-3 backdrop-blur-md border border-white/10 rounded-3xl p-6 sm:p-8 flex flex-col relative overflow-hidden" style={{ backgroundColor: 'white' }}>
                <div className="absolute bottom-0 right-0 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl"></div>

                <div className="flex items-center justify-between mb-6 relative z-10">
                  <div>
                    <h3 className="text-xl font-bold text-black flex items-center gap-3">
                      <FiTrendingUp className="text-purple-600" />
                      Traffic Analytics
                    </h3>
                    <p className="text-sm text-black mt-1">Real-time object detection distribution</p>
                  </div>
                  <div className="p-2 bg-slate-100 rounded-lg border border-slate-200">
                    <span className="text-xs font-semibold text-black">Live Targets</span>
                  </div>
                </div>

                <div className="flex-1 flex flex-col md:flex-row items-center gap-8 relative z-10 w-full mt-4 min-h-[300px]">
                  <div className="w-full md:w-1/2 flex justify-center items-center">
                    <PieChart
                      data={mockChartData}
                      colors={mockChartData.map(d => d.color)}
                      title=""
                      showCenterLabel={true}
                      textColor="black"
                    />
                  </div>
                  <div className="w-full md:w-1/2 space-y-4">
                    {mockChartData.map((item, i) => (
                      <div key={i} className="bg-slate-100 p-4 rounded-2xl border border-slate-200">
                        <div className="flex justify-between items-center mb-2">
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full shadow-[0_0_10px_rgba(255,255,255,0.2)]" style={{ backgroundColor: item.color }}></div>
                            <span className="text-sm font-medium text-black">{item.name}</span>
                          </div>
                          <span className="text-sm font-bold text-black">{item.value}%</span>
                        </div>
                        <div className="w-full bg-slate-300 rounded-full h-1.5 overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all duration-1000 ease-out"
                            style={{ width: `${item.value}%`, backgroundColor: item.color }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

            </div>
          </div>
        </main>
      </div>
    </div>

      {/* Modal Overlay */}
      {activeModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
          <div 
            className="absolute inset-0 bg-slate-950/60 backdrop-blur-md transition-opacity"
            onClick={() => setActiveModal(null)}
          ></div>
          
          <div className="relative w-full max-w-2xl bg-white rounded-3xl shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-300">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
              <h3 className="text-xl font-bold text-slate-900 flex items-center gap-3">
                {activeModal === 'settings' && <><FiSettings className="text-purple-500" /> System Settings</>}
                {activeModal === 'about' && <><FiInfo className="text-blue-500" /> About System</>}
                {activeModal === 'privacy' && <><FiShield className="text-emerald-500" /> Privacy & Security</>}
                {activeModal === 'notifications' && <><FiBell className="text-pink-500" /> All Notifications</>}
              </h3>
              <button 
                onClick={() => setActiveModal(null)}
                className="p-2 rounded-xl hover:bg-slate-200 text-slate-500 transition-colors"
              >
                <FiLogOut className="w-5 h-5 rotate-180" />
              </button>
            </div>

            <div className="p-6 max-h-[70vh] overflow-y-auto">
              {activeModal === 'settings' && (
                <div className="space-y-6">
                  <div className="space-y-4">
                    <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider">Interface Preferences</h4>
                    <div className="flex items-center justify-between p-4 bg-slate-50 rounded-2xl border border-slate-100">
                      <div>
                        <p className="font-semibold text-slate-900">High Contrast Mode</p>
                        <p className="text-xs text-slate-500">Enhance visibility for critical data</p>
                      </div>
                      <div className="w-12 h-6 bg-slate-200 rounded-full relative cursor-pointer">
                        <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full shadow-sm"></div>
                      </div>
                    </div>
                    <div className="flex items-center justify-between p-4 bg-slate-50 rounded-2xl border border-slate-100">
                      <div>
                        <p className="font-semibold text-slate-900">Auto-Refresh Interval</p>
                        <p className="text-xs text-slate-500">Real-time update frequency (seconds)</p>
                      </div>
                      <select className="bg-white border border-slate-200 rounded-lg px-2 py-1 text-sm font-medium text-slate-900">
                        <option>2s</option>
                        <option>5s</option>
                        <option>10s</option>
                      </select>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider">Alert Thresholds</h4>
                    <input type="range" className="w-full accent-purple-500" />
                    <p className="text-xs text-slate-500 italic">Sensitive detection may increase false positives.</p>
                  </div>
                </div>
              )}

              {activeModal === 'about' && (
                <div className="space-y-6 text-slate-900">
                  <div className="text-center pb-6 border-b border-slate-100">
                    <div className="w-24 h-24 mx-auto mb-4 flex items-center justify-center p-2">
                      <img src={mainLogo} alt="Official Logo" className="w-full h-full object-contain" />
                    </div>
                    <h4 className="text-2xl font-bold tracking-tight">CROWD & TRAFFIC CONTROL</h4>
                    <p className="text-slate-500 text-sm font-medium">Next-Generation Infrastructure Monitoring</p>
                  </div>
                  
                  <div className="space-y-4">
                    <h5 className="text-sm font-bold text-slate-400 uppercase tracking-widest">System Overview</h5>
                    <p className="text-sm text-slate-600 leading-relaxed">
                      Our <strong>Crowd & Traffic Control</strong> system is a comprehensive AI-driven platform designed to monitor and manage large-scale public environments in real-time. By leveraging advanced Object Detection Models (ODM), we provide actionable insights across three critical sectors:
                    </p>
                    <ul className="space-y-3">
                      <li className="flex gap-3 text-sm text-slate-700 bg-slate-50 p-3 rounded-xl border border-slate-100">
                        <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 shrink-0"></span>
                        <span><strong>Temple Management:</strong> Optimizing devotee flow and ensuring safety during high-density festivals and daily rituals.</span>
                      </li>
                      <li className="flex gap-3 text-sm text-slate-700 bg-slate-50 p-3 rounded-xl border border-slate-100">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-600 mt-1.5 shrink-0"></span>
                        <span><strong>Station Management:</strong> Monitoring platform congestion and transit entry points to prevent overcrowding and improve efficiency.</span>
                      </li>
                      <li className="flex gap-3 text-sm text-slate-700 bg-slate-50 p-3 rounded-xl border border-slate-100">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#6EC639] mt-1.5 shrink-0"></span>
                        <span><strong>Highway Monitoring:</strong> Real-time traffic analysis and surveillance to detect violations and manage toll plaza throughput.</span>
                      </li>
                    </ul>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                      <p className="text-[10px] text-slate-400 uppercase font-black mb-1 tracking-tighter">Engine Version</p>
                      <p className="font-bold text-slate-900">Vigilance AI v2.4.0</p>
                    </div>
                    <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                      <p className="text-[10px] text-slate-400 uppercase font-black mb-1 tracking-tighter">System Status</p>
                      <p className="font-bold text-emerald-600">FULLY OPERATIONAL</p>
                    </div>
                  </div>
                </div>
              )}

              {activeModal === 'privacy' && (
                <div className="space-y-6">
                  <div className="p-4 bg-emerald-50 border border-emerald-100 rounded-2xl flex items-start gap-4">
                    <FiShield className="w-6 h-6 text-emerald-500 shrink-0 mt-1" />
                    <div>
                      <p className="font-bold text-emerald-900">Data Encryption Active</p>
                      <p className="text-sm text-emerald-700">All camera feeds and metadata are encrypted with AES-256 standards during transmission and storage.</p>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider">Access Logs</h4>
                    {[
                      { user: 'Admin_01', action: 'Accessed Sector A1', time: '10:45 AM' },
                      { user: 'System', action: 'Purged logs older than 30d', time: '02:00 AM' },
                    ].map((log, i) => (
                      <div key={i} className="flex justify-between items-center p-3 bg-slate-50 rounded-xl">
                        <span className="text-sm font-medium text-slate-900"><b>{log.user}:</b> {log.action}</span>
                        <span className="text-xs text-slate-500">{log.time}</span>
                      </div>
                    ))}
                  </div>
                  <button className="w-full py-3 bg-slate-900 text-white rounded-xl font-bold hover:bg-slate-800 transition-colors">
                    Request Security Audit
                  </button>
                </div>
              )}

              {activeModal === 'notifications' && (
                <div className="space-y-4">
                  {[
                    { text: 'High congestion detected near Temple North Gate.', time: 'Just now', type: 'critical' },
                    { text: 'Unusual crowd density at Central Station platform 3.', time: '2m ago', type: 'warning' },
                    { text: 'Slow-moving traffic on Highway Sector A1.', time: '15m ago', type: 'info' },
                    { text: 'System Maintenance scheduled for 02:00 AM.', time: '1h ago', type: 'system' },
                    { text: 'Weather Alert: Heavy rain forecast at Bridge.', time: '3h ago', type: 'warning' },
                  ].map((alert, i) => (
                    <div key={i} className="flex gap-4 p-4 bg-slate-50 hover:bg-slate-100 rounded-2xl border border-slate-100 transition-colors cursor-pointer">
                      <div className={`w-2 h-10 rounded-full ${
                        alert.type === 'critical' ? 'bg-rose-500' :
                        alert.type === 'warning' ? 'bg-amber-500' : 
                        alert.type === 'system' ? 'bg-slate-900' : 'bg-blue-500'
                      }`}></div>
                      <div>
                        <p className="text-sm text-slate-900 font-bold mb-1">{alert.text}</p>
                        <p className="text-xs text-slate-500">{alert.time}</p>
                      </div>
                    </div>
                  ))}
                  <button className="w-full py-3 border-2 border-slate-200 text-slate-600 rounded-xl font-bold hover:bg-slate-50 transition-colors mt-4">
                    Clear All Notifications
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default HomeDashboard;

