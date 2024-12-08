import React, { useState } from "react";
import { Search } from "lucide-react";
import { PageContainer } from "../components/layout/PageContainer";

export function ScanPage() {
  const [ipAddress, setIpAddress] = useState("");

  const handleScan = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle scan logic here
    console.log("Scanning IP:", ipAddress);
  };

  return (
    <PageContainer title="Network Scanner">
      <div className="max-w-2xl mx-auto">
        <form
          onSubmit={handleScan}
          className="bg-white p-6 rounded-lg shadow-sm border"
        >
          <div className="mb-6">
            <label
              htmlFor="ipAddress"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              IP Address or Range
            </label>
            <div className="relative">
              <input
                type="text"
                id="ipAddress"
                value={ipAddress}
                onChange={(e) => setIpAddress(e.target.value)}
                placeholder="Enter IP address (e.g., 192.168.1.1) or range (e.g., 192.168.1.1-254)"
                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            </div>
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Start Scan
            </button>
          </div>
        </form>
      </div>
    </PageContainer>
  );
}
