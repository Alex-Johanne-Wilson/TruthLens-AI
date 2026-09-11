import React from 'react';
import { Award, ShieldCheck, HelpCircle, CheckCircle2, Clock } from 'lucide-react';

export default function TrustScoreGauge({ aiResult }) {
  // Multimodal trust score formula components
  const scoreVectors = [
    { name: 'AI Deep Convolution', weight: '30%', status: aiResult ? 'Evaluated' : 'Pending', active: !!aiResult },
    { name: 'Metadata & Container Coherence', weight: '20%', status: 'Pending Module', active: false },
    { name: 'Error Level Analysis (ELA)', weight: '15%', status: 'Pending Module', active: false },
    { name: 'Copy-Move Keypoint Matching', weight: '15%', status: 'Pending Module', active: false },
    { name: 'DCT Compression Grid Analysis', weight: '10%', status: 'Pending Module', active: false },
    { name: 'Deepfake Facial Biometrics', weight: '10%', status: 'Pending Module', active: false },
  ];

  return (
    <div className="cyber-card" style={{ marginBottom: '28px' }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid var(--border-subtle)',
        paddingBottom: '14px',
        marginBottom: '20px',
        flexWrap: 'wrap',
        gap: '8px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '6px',
            backgroundColor: 'rgba(0, 242, 254, 0.1)',
            border: '1px solid var(--border-cyan)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Award size={18} color="var(--cyber-cyan)" />
          </div>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: 700, margin: 0 }}>
              Digital Evidence Trust Score
            </h3>
            <span className="mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              UNIFIED MULTI-VECTOR AUTHENTICITY METRIC
            </span>
          </div>
        </div>

        <span className="badge badge-pending" style={{ fontSize: '9px' }}>
          AWAITING FULL PIPELINE
        </span>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'minmax(240px, 1fr) minmax(280px, 1.4fr)',
        gap: '28px',
        alignItems: 'center'
      }}>
        {/* Left: Circular Gauge Graphic */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '20px',
          backgroundColor: 'rgba(5, 8, 17, 0.5)',
          borderRadius: '12px',
          border: '1px solid var(--border-subtle)'
        }}>
          {/* Circular SVG Gauge */}
          <div style={{ position: 'relative', width: '160px', height: '160px' }}>
            <svg viewBox="0 0 100 100" style={{ transform: 'rotate(-90deg)', width: '100%', height: '100%' }}>
              {/* Background ring */}
              <circle
                cx="50"
                cy="50"
                r="40"
                fill="transparent"
                stroke="rgba(255, 255, 255, 0.06)"
                strokeWidth="8"
              />
              {/* Dashed pending ring */}
              <circle
                cx="50"
                cy="50"
                r="40"
                fill="transparent"
                stroke="rgba(0, 242, 254, 0.3)"
                strokeWidth="8"
                strokeDasharray="4 6"
              />
            </svg>

            {/* Center score readout */}
            <div style={{
              position: 'absolute',
              inset: 0,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              textAlign: 'center',
              padding: '10px'
            }}>
              <Clock size={20} color="var(--cyber-cyan)" style={{ marginBottom: '4px' }} />
              <div className="mono" style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-primary)' }}>
                -- / 100
              </div>
              <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                Trust Score
              </div>
            </div>
          </div>

          <div style={{
            fontSize: '12px',
            fontWeight: 600,
            color: 'var(--text-secondary)',
            textAlign: 'center',
            marginTop: '12px'
          }}>
            Awaiting forensic module integration
          </div>
          <div style={{ fontSize: '10px', color: 'var(--text-muted)', textAlign: 'center', marginTop: '2px' }}>
            Unified composite formula ready for backend weighting
          </div>
        </div>

        {/* Right: Vector breakdown */}
        <div>
          <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '10px' }}>
            Multi-Vector Evidence Weighting Schema:
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {scoreVectors.map((v) => (
              <div
                key={v.name}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '8px 12px',
                  borderRadius: '6px',
                  backgroundColor: v.active ? 'rgba(0, 242, 254, 0.06)' : 'rgba(255, 255, 255, 0.02)',
                  border: `1px solid ${v.active ? 'rgba(0, 242, 254, 0.25)' : 'var(--border-subtle)'}`,
                  fontSize: '12px'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  {v.active ? (
                    <CheckCircle2 size={14} color="var(--status-real)" />
                  ) : (
                    <Clock size={14} color="var(--text-muted)" />
                  )}
                  <span style={{ color: v.active ? 'var(--text-primary)' : 'var(--text-secondary)' }}>
                    {v.name}
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span className="mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                    Weight: {v.weight}
                  </span>
                  <span className={`badge ${v.active ? 'badge-real' : 'badge-pending'}`} style={{ fontSize: '8px' }}>
                    {v.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
