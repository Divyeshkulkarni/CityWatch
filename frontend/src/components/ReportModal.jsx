import React from 'react';
import { FiAlertCircle, FiClock, FiVideo, FiFileText, FiMapPin, FiActivity, FiShield, FiExternalLink } from 'react-icons/fi';
import driveLogo from '../../logo/drive .png';
import mainLogo from '../../logo/logo.png';

const ReportModal = ({ alert, onClose }) => {
  if (!alert) return null;

  const reportTime = "23:25:30"; // Report Generated Time
  const detectedTime = alert.time || "23:24:57";
  const preIncidentTime = "23:23:40";

  return (
    <div className="fixed inset-0 bg-slate-900/90 backdrop-blur-md flex items-center justify-center z-[100] p-4 font-sans" onClick={onClose}>
      <div 
        className="bg-white rounded-3xl w-full max-w-2xl shadow-[0_20px_50px_rgba(0,0,0,0.3)] overflow-hidden animate-in fade-in zoom-in duration-300"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header - Export Action */}
        <div className="bg-slate-50 px-8 py-4 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-red-100 flex items-center justify-center text-red-600">
              <span className="font-bold text-xs uppercase">PDF</span>
            </div>
            <span className="text-sm font-bold text-slate-500 uppercase tracking-widest">Incident Report Archive</span>
          </div>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-slate-200 rounded-full transition-colors text-slate-400 hover:text-slate-600"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* PDF Content Area */}
        <div className="p-8 space-y-8 max-h-[75vh] overflow-y-auto">
          
          {/* Brand Logo Header */}
          <div className="flex flex-col items-center justify-center pb-4 border-b border-slate-100">
            <img src={mainLogo} alt="Logo" className="w-16 h-16 object-contain mb-2" />
            <h2 className="text-xl font-black text-slate-900 tracking-tighter uppercase">CROWD & TRAFFIC CONTROL</h2>
            <p className="text-[10px] text-slate-400 font-bold tracking-[0.2em] uppercase mt-1">Vigilance Intelligence Report</p>
          </div>
          
          {/* Section 1: Incident Information */}
          <section className="space-y-4">
            <div className="flex items-center gap-3 text-slate-900">
              <FiAlertCircle className="w-5 h-5 text-indigo-600" />
              <h3 className="text-lg font-bold tracking-tight">Incident Information</h3>
            </div>
            <div className="h-px bg-slate-100 w-full"></div>
            
            <div className="grid grid-cols-2 gap-y-4">
              <div className="space-y-1">
                <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Alert Type</p>
                <p className="text-sm font-bold text-slate-800">{alert.title || "Temple Crowd Analysis Report"}</p>
              </div>
              <div className="space-y-1">
                <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Location</p>
                <p className="text-sm font-bold text-slate-800">{alert.location || "Temple Monitoring System"}</p>
              </div>
              <div className="space-y-1">
                <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Severity Level</p>
                <span className="inline-flex px-3 py-1 bg-yellow-400 text-gray-900 rounded-full text-xs font-black uppercase tracking-tighter">
                  {alert.severity || "MEDIUM"}
                </span>
              </div>
              <div className="space-y-1">
                <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Camera ID</p>
                <p className="text-sm font-bold text-slate-800">CAM-04 (Main Entrance)</p>
              </div>
            </div>
          </section>

          {/* Section 2: Time Details */}
          <section className="space-y-4">
            <div className="flex items-center gap-3 text-slate-900">
              <FiClock className="w-5 h-5 text-indigo-600" />
              <h3 className="text-lg font-bold tracking-tight">Time Details</h3>
            </div>
            <div className="h-px bg-slate-100 w-full"></div>
            
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-slate-50 p-3 rounded-2xl border border-slate-100">
                <p className="text-[9px] text-slate-400 font-bold uppercase mb-1">Incident Detected</p>
                <p className="text-sm font-mono font-bold text-slate-800">{detectedTime}</p>
              </div>
              <div className="bg-slate-50 p-3 rounded-2xl border border-slate-100">
                <p className="text-[9px] text-slate-400 font-bold uppercase mb-1">Pre-Incident Buffer</p>
                <p className="text-sm font-mono font-bold text-slate-800">{preIncidentTime}</p>
              </div>
              <div className="bg-slate-50 p-3 rounded-2xl border border-slate-100">
                <p className="text-[9px] text-slate-400 font-bold uppercase mb-1">Report Finalized</p>
                <p className="text-sm font-mono font-bold text-slate-800">{reportTime}</p>
              </div>
            </div>
          </section>

          {/* Section 3: Evidence */}
          <section className="space-y-4">
            <div className="flex items-center gap-3 text-slate-900">
              <FiVideo className="w-5 h-5 text-indigo-600" />
              <h3 className="text-lg font-bold tracking-tight">Evidence</h3>
            </div>
            <div className="h-px bg-slate-100 w-full"></div>
            
            <div className="p-4 bg-blue-50/50 border border-blue-100 rounded-2xl flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-white shadow-sm border border-blue-200 rounded-xl flex items-center justify-center p-1.5 overflow-hidden">
                  <img src={driveLogo} alt="Google Drive" className="w-full h-full object-contain" />
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-400 uppercase">Video Evidence Cloud Link</p>
                  <a href="#" className="text-sm font-bold text-blue-600 hover:text-blue-700 underline flex items-center gap-1">
                    vgs_secure_link_cam04_2324.mp4 <FiExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
              <span className="text-[10px] bg-blue-100 text-blue-600 font-black px-2 py-0.5 rounded">SECURE</span>
            </div>
          </section>

          {/* Section 4: AI Assessment */}
          <section className="space-y-4">
            <div className="flex items-center gap-3 text-slate-900">
              <FiFileText className="w-5 h-5 text-indigo-600" />
              <h3 className="text-lg font-bold tracking-tight">Incident Description & Recommended Action</h3>
            </div>
            <div className="h-px bg-slate-100 w-full"></div>
            
            <div className="space-y-4">
              <div className="p-5 bg-slate-50 rounded-2xl border border-slate-100">
                <h4 className="text-[10px] text-slate-400 font-bold uppercase mb-2">Detailed Narrative</h4>
                <p className="text-sm text-slate-600 leading-relaxed italic">
                  Advanced vision analysis detected abnormal density accumulation at the North Gate entrance. Flow rate decreased by 40% over a 3-minute window, indicating potential bottlenecking.
                </p>
              </div>
              <div className="p-5 bg-emerald-50 border border-emerald-100 rounded-2xl">
                <h4 className="text-[10px] text-emerald-600 font-bold uppercase mb-2 flex items-center gap-2">
                  <FiShield className="w-3 h-3" /> Action Plan
                </h4>
                <p className="text-sm text-emerald-900 font-bold">
                  Deploy ground personnel to Gate 4 immediately. Activate secondary exit channels for crowd diversion.
                </p>
              </div>
            </div>
          </section>
        </div>

        {/* Footer */}
        <div className="p-6 bg-slate-50 border-t border-slate-100 flex gap-4">
          <button 
            onClick={onClose}
            className="flex-1 py-3 bg-white border-2 border-slate-200 text-slate-600 rounded-2xl font-bold hover:bg-slate-50 transition-all text-sm uppercase tracking-widest"
          >
            DISMISS
          </button>
          <button 
            className="flex-1 py-3 bg-slate-900 text-white rounded-2xl font-bold hover:bg-slate-800 transition-all shadow-lg text-sm uppercase tracking-widest flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            DOWNLOAD COPY
          </button>
        </div>
      </div>
    </div>
  );
};

export default ReportModal;
