import React from 'react';
import { 
  ShieldCheck, 
  Image as ImageIcon, 
  Video, 
  UserCheck, 
  FileSearch, 
  FileText, 
  History, 
  Settings, 
  Info,
  Terminal,
  ExternalLink
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, backendStatus }) {
  const navItems = [
    { id: 'image', label: 'Image Analysis', icon: ImageIcon, badge: 'ACTIVE' },
    { id: 'video', label: 'Video Analysis', icon: Video, badge: 'BETA' },
    { id: 'deepfake', label: 'Deepfake Detection', icon: UserCheck, badge: 'PROTO' },
    { id: 'metadata', label: 'Metadata Analysis', icon: FileSearch, badge: null },
    { id: 'report', label: 'Forensic Report', icon: FileText, badge: null },
    { id: 'history', label: 'History & Vault', icon: History, badge: null },
  ];

  const secondaryNav = [
    { id: 'settings', label: 'Settings', icon: Settings },
    { id: 'about', label: 'About & Model Card', icon: Info },
  ];

  return (
    <aside style={{
      width: 'var(--sidebar-width)',
      backgroundColor: 'var(--bg-darker)',
      borderRight: '1px solid var(--border-subtle)',
      display: 'flex',
      flexDirection: 'column',
      flexShrink: 0,
      minHeight: '100vh',
      zIndex: 20
    }}>
      {/* Brand Header */}
      <div style={{
        padding: '24px 20px',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        flexDirection: 'column',
        gap: '6px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, rgba(0, 112, 243, 0.25) 0%, rgba(0, 242, 254, 0.25) 100%)',
            border: '1px solid var(--border-cyan)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: 'var(--shadow-cyan)'
          }}>
            <ShieldCheck size={22} color="var(--cyber-cyan)" />
          </div>
          <div>
            <div style={{
              fontFamily: 'var(--font-heading)',
              fontSize: '20px',
              fontWeight: 800,
              letterSpacing: '-0.03em',
              lineHeight: 1.1,
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <span>Truth</span>
              <span className="text-gradient-cyan">Lens</span>
            </div>
            <div style={{
              fontSize: '10px',
              fontWeight: 600,
              color: 'var(--text-muted)',
              letterSpacing: '0.08em',
              textTransform: 'uppercase'
            }}>
              Forensic Suite v1.0
            </div>
          </div>
        </div>

        <div style={{
          fontSize: '11px',
          color: 'var(--text-secondary)',
          fontStyle: 'italic',
          marginTop: '4px'
        }}>
          Digital Evidence. Real Trust.
        </div>
      </div>

      {/* Main Navigation */}
      <nav style={{
        padding: '18px 12px',
        display: 'flex',
        flexDirection: 'column',
        gap: '4px',
        flex: 1
      }}>
        <div style={{
          fontSize: '10px',
          fontWeight: 700,
          color: 'var(--text-muted)',
          textTransform: 'uppercase',
          letterSpacing: '0.1em',
          padding: '4px 12px 8px 12px'
        }}>
          Forensic Modules
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '10px 14px',
                borderRadius: '8px',
                border: isActive ? '1px solid var(--border-cyan)' : '1px solid transparent',
                backgroundColor: isActive ? 'rgba(0, 242, 254, 0.08)' : 'transparent',
                color: isActive ? 'var(--cyber-cyan)' : 'var(--text-secondary)',
                fontSize: '13px',
                fontWeight: isActive ? 600 : 500,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                width: '100%',
                textAlign: 'left'
              }}
              onMouseEnter={(e) => {
                if (!isActive) {
                  e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.03)';
                  e.currentTarget.style.color = 'var(--text-primary)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive) {
                  e.currentTarget.style.backgroundColor = 'transparent';
                  e.currentTarget.style.color = 'var(--text-secondary)';
                }
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Icon size={18} color={isActive ? 'var(--cyber-cyan)' : 'currentColor'} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span style={{
                  fontSize: '9px',
                  fontWeight: 700,
                  padding: '2px 6px',
                  borderRadius: '4px',
                  backgroundColor: item.badge === 'ACTIVE' 
                    ? 'rgba(16, 185, 129, 0.15)' 
                    : 'rgba(56, 189, 248, 0.15)',
                  color: item.badge === 'ACTIVE' ? 'var(--status-real)' : 'var(--cyber-cyan)',
                  border: `1px solid ${item.badge === 'ACTIVE' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(56, 189, 248, 0.3)'}`
                }}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}

        <div style={{
          fontSize: '10px',
          fontWeight: 700,
          color: 'var(--text-muted)',
          textTransform: 'uppercase',
          letterSpacing: '0.1em',
          padding: '16px 12px 8px 12px'
        }}>
          System & Config
        </div>

        {secondaryNav.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '10px 14px',
                borderRadius: '8px',
                border: isActive ? '1px solid var(--border-cyan)' : '1px solid transparent',
                backgroundColor: isActive ? 'rgba(0, 242, 254, 0.08)' : 'transparent',
                color: isActive ? 'var(--cyber-cyan)' : 'var(--text-secondary)',
                fontSize: '13px',
                fontWeight: isActive ? 600 : 500,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                width: '100%',
                textAlign: 'left'
              }}
              onMouseEnter={(e) => {
                if (!isActive) {
                  e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.03)';
                  e.currentTarget.style.color = 'var(--text-primary)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive) {
                  e.currentTarget.style.backgroundColor = 'transparent';
                  e.currentTarget.style.color = 'var(--text-secondary)';
                }
              }}
            >
              <Icon size={18} color={isActive ? 'var(--cyber-cyan)' : 'currentColor'} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Telemetry Footer */}
      <div style={{
        padding: '16px 18px',
        borderTop: '1px solid var(--border-subtle)',
        backgroundColor: 'rgba(5, 8, 17, 0.4)',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '11px'
        }}>
          <span style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Terminal size={12} />
            ENGINE
          </span>
          <span className="mono" style={{ color: 'var(--cyber-cyan)', fontWeight: 600 }}>
            EfficientNet-B0
          </span>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '11px'
        }}>
          <span style={{ color: 'var(--text-muted)' }}>BACKEND</span>
          <span style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            color: backendStatus?.ok ? 'var(--status-real)' : 'var(--status-ai)',
            fontWeight: 600,
            fontSize: '10px'
          }}>
            <span className={`pulse-dot ${backendStatus?.ok ? 'pulse-dot-green' : 'pulse-dot-red'}`} />
            {backendStatus?.ok ? '127.0.0.1:8000' : 'OFFLINE'}
          </span>
        </div>
      </div>
    </aside>
  );
}
