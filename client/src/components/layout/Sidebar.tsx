import React from 'react';
import { BarChart3, Search, Settings, Shield, Terminal } from 'lucide-react';
import { NavLink } from './NavLink';

export function Sidebar() {
  return (
    <div className="h-screen w-64 bg-gray-900 text-white p-4 fixed left-0 top-0">
      <div className="flex items-center gap-2 mb-8">
        <Shield className="w-8 h-8 text-blue-400" />
        <span className="text-xl font-bold">NetScan</span>
      </div>
      
      <nav className="space-y-2">
        <NavLink to="/dashboard" icon={BarChart3}>Dashboard</NavLink>
        <NavLink to="/scan" icon={Search}>Scan</NavLink>
        <NavLink to="/logs" icon={Terminal}>Logs</NavLink>
        <NavLink to="/settings" icon={Settings}>Settings</NavLink>
      </nav>
    </div>
  );
}