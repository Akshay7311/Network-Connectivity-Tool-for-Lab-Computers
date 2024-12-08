export interface ScanResult {
  id: string;
  ipAddress: string;
  status: 'open' | 'closed' | 'filtered';
  ports: Port[];
  timestamp: string;
  vulnerabilities: Vulnerability[];
  os?: string;
  hostname?: string;
  lastSeen?: string;
}

export interface Port {
  number: string;
  service?: string;
  version?: string;
  state: 'open' | 'closed' | 'filtered';
}

export interface Vulnerability {
  id: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
}