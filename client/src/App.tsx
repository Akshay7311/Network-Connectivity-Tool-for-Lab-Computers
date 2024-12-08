import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Header } from './components/layout/Header';
import { Sidebar } from './components/layout/Sidebar';
import { ScanTable } from './components/scan/ScanTable';
import { PageContainer } from './components/layout/PageContainer';
import { ScanPage } from './pages/ScanPage';
import { LogsPage } from './pages/LogsPage';
import { LoginPage } from './pages/LoginPage';
import { ProtectedRoute } from './components/auth/ProtectedRoute';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <div className="min-h-screen bg-gray-50">
                <Sidebar />
                <div className="ml-64">
                  <Header />
                  <main className="pt-16">
                    <Routes>
                      <Route path="/" element={<Navigate to="/dashboard" replace />} />
                      <Route
                        path="/dashboard"
                        element={
                          <PageContainer title="Network Scan Results">
                            <ScanTable />
                          </PageContainer>
                        }
                      />
                      <Route path="/scan" element={<ScanPage />} />
                      <Route path="/logs" element={<LogsPage />} />
                      <Route
                        path="/settings"
                        element={
                          <PageContainer title="Settings">
                            <div className="bg-white p-6 rounded-lg shadow-sm border">
                              <p>Settings page content will go here.</p>
                            </div>
                          </PageContainer>
                        }
                      />
                    </Routes>
                  </main>
                </div>
              </div>
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;