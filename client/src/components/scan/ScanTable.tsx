import React, { useState } from 'react';
import { Clock, Shield, Wifi } from 'lucide-react';
import { ScanResult } from '../../types/scan';
import { ScanDetailsDialog } from './ScanDetailsDialog';

const mockData: ScanResult[] = [
  {
    id: '1',
    ipAddress: '192.168.1.1',
    status: 'open',
    ports: [
      { number: '80', service: 'HTTP', version: 'Apache/2.4.41', state: 'open' },
      { number: '443', service: 'HTTPS', version: 'nginx/1.18.0', state: 'open' },
      { number: '22', service: 'SSH', version: 'OpenSSH 8.2p1', state: 'open' }
    ],
    timestamp: '2024-03-15 14:30',
    hostname: 'gateway.local',
    os: 'Linux 5.4.0',
    lastSeen: '2024-03-15 14:30',
    vulnerabilities: [
      {
        id: 'CVE-2024-1234',
        severity: 'high',
        title: 'Apache HTTP Server Buffer Overflow',
        description: 'A buffer overflow vulnerability in Apache HTTP Server allows remote attackers to execute arbitrary code.'
      },
      {
        id: 'CVE-2024-5678',
        severity: 'medium',
        title: 'OpenSSH Authentication Bypass',
        description: 'An authentication bypass vulnerability in OpenSSH could allow unauthorized access.'
      }
    ]
  },
  {
    id: '2',
    ipAddress: '192.168.1.2',
    status: 'closed',
    ports: [
      { number: '80', service: 'HTTP', state: 'closed' }
    ],
    timestamp: '2024-03-15 14:25',
    vulnerabilities: []
  }
];

export function ScanTable() {
  const [selectedScan, setSelectedScan] = useState<ScanResult | null>(null);

  return (
    <>
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 border-b">
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">IP Address</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Open Ports</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Scan Time</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vulnerabilities</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {mockData.map((result) => (
                <tr 
                  key={result.id} 
                  className="hover:bg-gray-50 cursor-pointer" 
                  onClick={() => setSelectedScan(result)}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <Wifi className="w-4 h-4 text-gray-400" />
                      <span>{result.ipAddress}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      result.status === 'open' ? 'bg-green-100 text-green-800' :
                      result.status === 'closed' ? 'bg-red-100 text-red-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {result.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex gap-1">
                      {result.ports.map((port) => (
                        <span key={port.number} className="bg-gray-100 px-2 py-1 rounded text-sm">
                          {port.number}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2 text-gray-500">
                      <Clock className="w-4 h-4" />
                      <span>{result.timestamp}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <Shield className={`w-4 h-4 ${
                        result.vulnerabilities.length === 0 ? 'text-green-500' :
                        result.vulnerabilities.length < 3 ? 'text-yellow-500' :
                        'text-red-500'
                      }`} />
                      <span>{result.vulnerabilities.length}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {selectedScan && (
        <ScanDetailsDialog 
          scan={selectedScan} 
          onClose={() => setSelectedScan(null)} 
        />
      )}
    </>
  );
}