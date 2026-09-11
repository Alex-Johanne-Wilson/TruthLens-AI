import React, { useState } from 'react';
import { 
  Bell, 
  User, 
  Activity, 
  RefreshCw, 
  Sun, 
  Moon, 
  ChevronRight,
  Shield,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

export default function Header({ 
  activeTab, 
  backendStatus, 
  onRefreshHealth,
  isRefreshingHealth 
}) {
  const [highContrast, setHighContrast] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  const tabTitles = {
    image: 'Image Forensics & AI Detection',
    video: 'Video Forensics Analysis',
    deepfake: 'Deepfake Biometric Detection',
    metadata: 'EXIF & Digital Metadata Analysis',
    report: 'Digital Evidence Forensic Report',
    history: 'Evidence Vault & Analysis History',
    settings: 'Forensic System Settings',
    about: 'Model Architecture & Documentation',
  };

  const notifications = [
    { id: 1, title: 'Inference Ready', desc: 'EfficientNet-B0 detector active on port 8000', time: '1m ago', unread: true },
    { id: 2, title: 'Grad-CAM Calibrated', desc: 'Feature map extraction hooked to model features layer', time: '5m ago', unread: false },
    { id: 3, title: 'Audit Checkpoint', desc: 'SHA-256 integrity verified for best_model.pth', time: '15m ago', unread: false },
  ];

  return (
    <header style={{
      height: 'var(--header-height)',
      backgroundColor: 'var(--bg-glass)',
      backdropFilter: 'blur(16px)',
      WebkitBackdropFilter: 'blur(16px)',
      borderBottom: '1px solid var(--border-subtle)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 28px',
      position: 'sticky',
      top: 0,
      zIndex: 15
    }}>
      {/* Left: Breadcrumbs & Active Title */}
      <div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '11px',
          color: 'var(--text-muted)',
          marginBottom: '2px'
        }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Shield size={12} color="var(--cyber-cyan)" />
            TRUTHLENS EVIDENCE SUITE
          </span>
          <ChevronRight size={12} />
          <span style={{ color: 'var(--cyber-cyan)', fontWeight: 600 }}>
            {activeTab.toUpperCase()}
          </span>
        </div>
        <h1 style={{
          fontSize: '18px',
          fontWeight: 700,
          color: 'var(--text-primary)',
          letterSpacing: '-0.01em',
          margin: 0
        }}>
          {tabTitles[activeTab] || 'Forensic Workspace'}
        </h1>
      </div>

      {/* Right: Telemetry, Backend Health, Profile */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {/* Backend Live Indicator */}
        <div 
          onClick={onRefreshHealth}
          title="Click to re-ping backend server"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '6px 12px',
            borderRadius: '9999px',
            backgroundColor: backendStatus?.ok ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.1)',
            border: `1px solid ${backendStatus?.ok ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }}
        >
          <span className={`pulse-dot ${backendStatus?.ok ? 'pulse-dot-green' : 'pulse-dot-red'}`} />
          <span className="mono" style={{
            fontSize: '11px',
            fontWeight: 600,
            color: backendStatus?.ok ? 'var(--status-real)' : 'var(--status-ai)'
          }}>
            {backendStatus?.ok ? 'API 8000 ONLINE' : 'API 8000 DISCONNECTED'}
          </span>
          <RefreshCw 
            size={12} 
            color={backendStatus?.ok ? 'var(--status-real)' : 'var(--status-ai)'}
            style={{
              animation: isRefreshingHealth ? 'spin 1s linear infinite' : 'none'
            }}
          />
        </div>

        {/* Theme Contrast Switcher */}
        <button
          onClick={() => {
            setHighContrast(!highContrast);
            document.body.classList.toggle('high-contrast');
          }}
          title={highContrast ? "Switch to Cyber Dark Mode" : "Switch to High Contrast Midnight"}
          className="btn-ghost"
          style={{ padding: '8px', borderRadius: '8px' }}
        >
          {highContrast ? <Sun size={17} color="var(--cyber-cyan)" /> : <Moon size={17} />}
        </button>

        {/* Notification Icon */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="btn-ghost"
            style={{ padding: '8px', borderRadius: '8px', position: 'relative' }}
            title="System alerts & logs"
          >
            <Bell size={17} />
            <span style={{
              position: 'absolute',
              top: '6px',
              right: '6px',
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              backgroundColor: 'var(--cyber-cyan)',
              boxShadow: '0 0 6px var(--cyber-cyan)'
            }} />
          </button>

          {showNotifications && (
            <div 
              className="cyber-card" 
              style={{
                position: 'absolute',
                right: 0,
                top: '44px',
                width: '320px',
                padding: '16px',
                zIndex: 100,
                boxShadow: 'var(--shadow-lg)'
              }}
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingBottom: '10px',
                borderBottom: '1px solid var(--border-subtle)',
                marginBottom: '10px'
              }}>
                <span style={{ fontWeight: 700, fontSize: '13px' }}>System Telemetry Logs</span>
                <span className="badge badge-cyan" style={{ fontSize: '9px' }}>3 Active</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {notifications.map((n) => (
                  <div key={n.id} style={{
                    padding: '8px 10px',
                    borderRadius: '6px',
                    backgroundColor: 'rgba(255, 255, 255, 0.02)',
                    border: '1px solid var(--border-subtle)'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', fontWeight: 600 }}>
                      <span>{n.title}</span>
                      <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>{n.time}</span>
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                      {n.desc}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* User / Examiner Profile Badge */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          padding: '6px 12px',
          borderRadius: '8px',
          backgroundColor: 'rgba(15, 23, 42, 0.6)',
          border: '1px solid var(--border-subtle)'
        }}>
          <div style={{
            width: '28px',
            height: '28px',
            borderRadius: '6px',
            backgroundColor: 'rgba(0, 112, 243, 0.2)',
            border: '1px solid var(--border-cyan)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <User size={15} color="var(--cyber-cyan)" />
          </div>
          <div style={{ lineHeight: 1.2 }}>
            <div style={{ fontSize: '12px', fontWeight: 600 }}>Lead Examiner</div>
            <div style={{ fontSize: '10px', color: 'var(--cyber-cyan)' }}>Clearance LVL-4</div>
          </div>
        </div>
      </div>
    </header>
  );
}
