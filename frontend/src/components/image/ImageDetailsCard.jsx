import React from 'react';
import { FileCode, Clock, HardDrive, Cpu, FileType, CheckSquare } from 'lucide-react';

export default function ImageDetailsCard({ file, dimensions, analysisTimestamp }) {
  if (!file) return null;

  const formatBytes = (bytes) => {
    if (!bytes || bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const details = [
    { label: 'File Name', value: file.name, icon: FileCode, mono: true },
    { label: 'File Size', value: formatBytes(file.size), icon: HardDrive, mono: true },
    { label: 'Dimensions', value: dimensions ? `${dimensions.width} × ${dimensions.height} px` : '224 × 224 (Normalized)', icon: CheckSquare, mono: true },
    { label: 'File Type', value: file.type || 'image/jpeg', icon: FileType, mono: true },
    { label: 'Analysis Time', value: analysisTimestamp || new Date().toISOString().replace('T', ' ').slice(0, 19) + ' UTC', icon: Clock, mono: true },
    { label: 'Model Used', value: 'EfficientNet-B0 (TruthLens)', icon: Cpu, mono: false, highlight: true },
  ];

  return (
    <div className="cyber-card" style={{ marginBottom: '28px' }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid var(--border-subtle)',
        paddingBottom: '14px',
        marginBottom: '18px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            DIGITAL EVIDENCE DOSSIER // TECHNICAL ARTIFACT PROPERTIES
          </span>
        </div>
        <span className="badge badge-cyan" style={{ fontSize: '9px' }}>
          EVIDENCE METRICS
        </span>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '16px'
      }}>
        {details.map((item) => {
          const Icon = item.icon;
          return (
            <div
              key={item.label}
              style={{
                backgroundColor: 'rgba(5, 8, 17, 0.45)',
                padding: '12px 14px',
                borderRadius: '8px',
                border: '1px solid var(--border-subtle)',
                display: 'flex',
                flexDirection: 'column',
                gap: '4px'
              }}
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '11px',
                color: 'var(--text-muted)'
              }}>
                <Icon size={13} color="var(--cyber-cyan)" />
                <span>{item.label}</span>
              </div>

              <div 
                className={item.mono ? 'mono' : ''}
                style={{
                  fontSize: '13px',
                  fontWeight: 600,
                  color: item.highlight ? 'var(--cyber-cyan)' : 'var(--text-primary)',
                  wordBreak: 'break-all'
                }}
              >
                {item.value}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
