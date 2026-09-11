import React, { useState } from 'react';
import { Settings, Server, Sliders, ShieldCheck, Database, Check } from 'lucide-react';

export default function SettingsView({ backendStatus, onRefreshHealth }) {
  const [apiEndpoint, setApiEndpoint] = useState('http://127.0.0.1:8000');
  const [confidenceThreshold, setConfidenceThreshold] = useState(50);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 2000);
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ marginBottom: '28px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <Settings size={18} color="var(--cyber-cyan)" />
          <span className="mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            SYSTEM CONFIGURATION // LOCAL ENVIRONMENT
          </span>
        </div>
        <h2 style={{ fontSize: '28px', fontWeight: 800, margin: 0 }}>
          Forensic System Settings
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginTop: '4px' }}>
          Configure API endpoints, inference confidence thresholds, and forensic logging defaults.
        </p>
      </div>

      <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {/* API Backend Connection */}
        <div className="cyber-card">
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: '1px solid var(--border-subtle)',
            paddingBottom: '12px',
            marginBottom: '16px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Server size={16} color="var(--cyber-cyan)" />
              <h4 style={{ fontSize: '14px', margin: 0 }}>FastAPI Backend Endpoint</h4>
            </div>
            <span className={`badge ${backendStatus?.ok ? 'badge-real' : 'badge-ai'}`}>
              {backendStatus?.ok ? 'CONNECTED' : 'OFFLINE'}
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Inference Server URL:
            </label>
            <div style={{ display: 'flex', gap: '10px' }}>
              <input
                type="text"
                value={apiEndpoint}
                onChange={(e) => setApiEndpoint(e.target.value)}
                style={{
                  flex: 1,
                  backgroundColor: 'rgba(5, 8, 17, 0.6)',
                  border: '1px solid var(--border-cyan)',
                  borderRadius: '6px',
                  padding: '10px 14px',
                  color: 'var(--text-primary)',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '13px',
                  outline: 'none'
                }}
              />
              <button
                type="button"
                onClick={onRefreshHealth}
                className="btn-secondary"
                style={{ fontSize: '12px' }}
              >
                Ping Health
              </button>
            </div>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              Default: <code>http://127.0.0.1:8000</code>. Verified routes: <code>/health</code>, <code>/api/analyze/image</code>, <code>/api/analyze/deepfake</code>
            </span>
          </div>
        </div>

        {/* Classification Sensitivity */}
        <div className="cyber-card">
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            borderBottom: '1px solid var(--border-subtle)',
            paddingBottom: '12px',
            marginBottom: '16px'
          }}>
            <Sliders size={16} color="var(--cyber-cyan)" />
            <h4 style={{ fontSize: '14px', margin: 0 }}>Inference Sensitivity Threshold</h4>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
              <span style={{ color: 'var(--text-secondary)' }}>AI Classification Cutoff:</span>
              <span className="mono" style={{ color: 'var(--cyber-cyan)', fontWeight: 700 }}>
                {confidenceThreshold}%
              </span>
            </div>

            <input
              type="range"
              min="10"
              max="90"
              value={confidenceThreshold}
              onChange={(e) => setConfidenceThreshold(Number(e.target.value))}
              style={{ accentColor: 'var(--cyber-cyan)' }}
            />

            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              Determines the decision boundary threshold applied when evaluating softmax probabilities.
            </span>
          </div>
        </div>

        {/* Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button type="submit" className="btn-primary" style={{ padding: '10px 24px' }}>
            {saveSuccess ? (
              <>
                <Check size={16} /> Saved!
              </>
            ) : (
              'Save Preferences'
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
