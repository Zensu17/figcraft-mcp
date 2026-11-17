import React from 'react';

export default function WeatherWidget() {
  return (
    <div className="flex items-center justify-center p-6 bg-slate-950 min-h-screen">
      {/* Simple Weather Widget */}
      <div className="flex flex-col p-[20px] gap-[10px] bg-[#1E293B] rounded-[20px]">
        <span className="text-xs text-[#94A3B8]">📍 Jakarta, Indonesia</span>
        {/* Temperature Row */}
      <div className="flex flex-row gap-[12px] items-center">
        <span className="text-3xl font-extrabold text-[#F8FAFC]">29°C</span>
        <span className="text-sm text-[#38BDF8]">⛅ Sebagian Berawan</span>
      </div>
        {/* Metrics Row */}
      <div className="flex flex-row justify-between items-center">
        <span className="text-xs text-[#94A3B8]">💧 78%</span>
        <span className="text-xs text-[#94A3B8]">💨 14 km/j</span>
        <span className="text-xs text-[#94A3B8]">☀️ UV Sedang</span>
      </div>
      </div>
    </div>
  );
}
