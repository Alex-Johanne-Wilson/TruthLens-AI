import React from 'react';
import { 
  ShieldAlert, 
  Activity, 
  Layers, 
  Maximize, 
  Palette, 
  Copy, 
  FileCheck,
  AlertCircle
} from 'lucide-react';

export default function ForensicChecksGrid() {
  const modules = [
    {
      id: 'noise',
      name: 'Noise Analysis',
      description: 'Variance in sensor PRNU pattern & spatial noise residue',
      icon: Activity,
      status: 'Pending Integration',
      target: 'Sensor Grain Discrepancies'
    },
    {
      id: 'compression',
      name: 'Compression Check',
      description: 'Discrete Cosine Transform (DCT) grid alignment & quantization',
      icon: Layers,
      status: 'Pending Integration',
      target: 'Double JPEG Compression'
    },
    {
      id: 'edge',
      name: 'Edge Artifacts',
      description: 'Boundary gradient transitions & blending discontinuity',
      icon: Maximize,
      status: 'Pending Integration',
      target: 'Inpainting & Cutout Halos'
    },
    {
      id: 'color',
      name: 'Color Consistency',
      description: 'Chrominance distribution & illuminant direction coherence',
      icon: Palette,
      status: 'Pending Integration',
      target: 'Lighting Vector Mismatch'
    },
    {
      id: 'copymove',
      name: 'Copy-Move Detection',
      description: 'Keypoint SIFT/SURF clone block matching across regions',
      icon: Copy,
      status: 'Pending Integration',
      target: 'Cloned Object Duplication'
    },
    {
      id: 'ela',
      name: 'ELA Analysis',
      description: 'Error Level Analysis highlighting resaved compression delta',
      icon: FileCheck,
      status: 'Pending Integration',
      target: 'Local Error Rate Peaks'
    },
  ];

  return (
    <div className="cyber-card" style={{ marginBottom: '28px' }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid var(--border-subtle)',
        paddingBottom: '14px',
        marginBottom: '18px',
        flexWrap: 'wrap',
        gap: '8px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '6px',
            backgroundColor: 'rgba(56, 189, 248, 0.1)',
            border: '1px solid var(--border-cyan)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <ShieldAlert size={18} color="var(--cyber-cyan)" />
          </div>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: 700, margin: 0 }}>
              Multi-Layer Forensic Checks
            </h3>
            <span className="mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              CLASSICAL FORENSIC SUITE // ALEC HOOK ARCHITECTURE
            </span>
          </div>
        </div>

        <span className="badge badge-pending" style={{ fontSize: '9px' }}>
          6 CHECKS PENDING INTEGRATION
        </span>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
        gap: '16px'
      }}>
        {modules.map((mod) => {
          const Icon = mod.icon;
          return (
            <div
              key={mod.id}
              style={{
                backgroundColor: 'rgba(5, 8, 17, 0.5)',
                borderRadius: '8px',
                border: '1px solid var(--border-subtle)',
                padding: '16px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                gap: '12px',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'rgba(100, 116, 139, 0.4)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--border-subtle)';
              }}
            >
              <div>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '8px'
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    fontWeight: 700,
                    fontSize: '13px',
                    color: 'var(--text-primary)'
                  }}>
                    <Icon size={15} color="var(--text-accent)" />
                    <span>{mod.name}</span>
                  </div>
                  <span className="badge badge-pending" style={{ fontSize: '8px' }}>
                    {mod.status}
                  </span>
                </div>

                <div style={{ fontSize: '11px', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                  {mod.description}
                </div>
              </div>

              <div style={{
                paddingTop: '8px',
                borderTop: '1px solid rgba(255, 255, 255, 0.04)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                fontSize: '10px',
                color: 'var(--text-muted)'
              }}>
                <span>Target Vector:</span>
                <span className="mono" style={{ color: 'var(--text-secondary)' }}>
                  {mod.target}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
