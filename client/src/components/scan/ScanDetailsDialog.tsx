import React from 'react';
import { X } from 'lucide-react';
import { ScanResult } from '../../types/scan';

interface ScanDetailsDialogProps {
  scan: ScanResult;
  onClose: () => void;
}

export function ScanDetailsDialog({ scan, onClose }: ScanDetailsDialogProps) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b p-4 flex items-center justify-between">
          <h2 className="text-xl font-bold">Scan Details: {scan.ipAddress}</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-full">
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="p-6 space-y-6">
          {/* Basic Information */}
          <section>
            <h3 className="text-lg font-semibold mb-3">Basic Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Hostname</p>
                <p className="font-medium">{scan.hostname || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Operating System</p>
                <p className="font-medium">{scan.os || 'Unknown'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Last Seen</p>
                <p className="font-medium">{scan.lastSeen || scan.timestamp}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Status</p>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  scan.status === 'open' ? 'bg-green-100 text-green-800' :
                  scan.status === 'closed' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {scan.status}
                </span>
              </div>
            </div>
          </section>

          {/* Ports */}
          <section>
            <h3 className="text-lg font-semibold mb-3">Open Ports</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead>
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Port</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Service</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Version</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">State</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {scan.ports.map((port) => (
                    <tr key={port.number}>
                      <td className="px-4 py-2">{port.number}</td>
                      <td className="px-4 py-2">{port.service || 'Unknown'}</td>
                      <td className="px-4 py-2">{port.version || 'N/A'}</td>
                      <td className="px-4 py-2">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                          port.state === 'open' ? 'bg-green-100 text-green-800' :
                          port.state === 'closed' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {port.state}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {/* Vulnerabilities */}
          {scan.vulnerabilities.length > 0 && (
            <section>
              <h3 className="text-lg font-semibold mb-3">Vulnerabilities</h3>
              <div className="space-y-4">
                {scan.vulnerabilities.map((vuln) => (
                  <div key={vuln.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{vuln.title}</h4>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        vuln.severity === 'critical' ? 'bg-red-100 text-red-800' :
                        vuln.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                        vuln.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {vuln.severity}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">{vuln.description}</p>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  );
}