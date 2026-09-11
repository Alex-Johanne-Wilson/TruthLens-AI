import React, { useState, useEffect } from 'react';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import ImageAnalysisView from './components/image/ImageAnalysisView';
import DeepfakeView from './components/deepfake/DeepfakeView';
import ReportView from './components/report/ReportView';
import HistoryView from './components/history/HistoryView';
import MetadataView from './components/metadata/MetadataView';
import SettingsView from './components/settings/SettingsView';
import AboutView from './components/about/AboutView';
import { checkBackendHealth } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('image');
  const [backendStatus, setBackendStatus] = useState({ ok: false, checked: false });
  const [isRefreshingHealth, setIsRefreshingHealth] = useState(false);

  // Cross-view evidence state
  const [currentEvidence, setCurrentEvidence] = useState(null);
  const [lastResult, setLastResult] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  const fetchHealth = async () => {
    setIsRefreshingHealth(true);
    const res = await checkBackendHealth();
    setBackendStatus({ ok: res.ok, status: res.status, checked: true });
    setIsRefreshingHealth(false);
  };

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleRecordHistory = (item) => {
    try {
      const stored = localStorage.getItem('truthlens_history');
      const existing = stored ? JSON.parse(stored) : [];
      const updated = [item, ...existing];
      localStorage.setItem('truthlens_history', JSON.stringify(updated.slice(0, 50)));
    } catch (e) {
      console.error('Failed saving to history:', e);
    }
  };

  const handleViewReport = (file, result, url) => {
    setCurrentEvidence(file);
    setLastResult(result);
    setPreviewUrl(url);
    setActiveTab('report');
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', width: '100%', backgroundColor: 'var(--bg-darkest)' }}>
      {/* Persistent Left Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        backendStatus={backendStatus}
      />

      {/* Main Content Area */}
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        minWidth: 0,
        overflowY: 'auto'
      }}>
        {/* Top Header */}
        <Header
          activeTab={activeTab}
          backendStatus={backendStatus}
          onRefreshHealth={fetchHealth}
          isRefreshingHealth={isRefreshingHealth}
        />

        {/* Dynamic Page Views */}
        <main style={{ flex: 1, padding: '32px 36px' }}>
          {activeTab === 'image' && (
            <ImageAnalysisView
              onViewReport={handleViewReport}
              backendOnline={backendStatus.ok}
              onRecordHistory={handleRecordHistory}
              persistedEvidence={currentEvidence}
              persistedResult={lastResult}
            />
          )}

          {(activeTab === 'video' || activeTab === 'deepfake') && (
            <DeepfakeView />
          )}

          {activeTab === 'metadata' && (
            <MetadataView />
          )}

          {activeTab === 'report' && (
            <ReportView
              currentEvidence={currentEvidence}
              lastResult={lastResult}
              previewUrl={previewUrl}
            />
          )}

          {activeTab === 'history' && (
            <HistoryView
              onSelectEvidence={(item) => {
                // Navigate to report with selected item
                setLastResult(item.result || {
                  predicted_class: item.verdict,
                  confidence: item.confidence / 100,
                  real_probability: item.verdict === 'real' ? 0.9998 : 0.0001,
                  ai_probability: item.verdict === 'ai_generated' ? 0.9985 : 0.0002,
                  gradcam_path: item.gradcam_path
                });
                setCurrentEvidence({ name: item.filename, size: 84509, type: 'image/jpeg' });
                setActiveTab('report');
              }}
            />
          )}

          {activeTab === 'settings' && (
            <SettingsView
              backendStatus={backendStatus}
              onRefreshHealth={fetchHealth}
            />
          )}

          {activeTab === 'about' && (
            <AboutView />
          )}
        </main>
      </div>
    </div>
  );
}
