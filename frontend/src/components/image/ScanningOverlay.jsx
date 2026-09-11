import React, { useState, useEffect } from 'react';
import { Scan, Cpu, Layers, FileSearch, ShieldCheck, Activity } from 'lucide-react';

export default function ScanningOverlay({ previewUrl, filename }) {
  const [currentStageIndex, setCurrentStageIndex] = useState(0);

  const stages = [
    { label: 'File Preprocessing & Normalization', icon: Scan, detail: 'Resizing to 224x224 & RGB PyTorch Tensor' },
    { label: 'EfficientNet-B0 AI Feature Extraction', icon: Cpu, detail: 'Running convolution kernels on backend' },
    { label: 'Grad-CAM Activation Mapping', icon: Layers, detail: 'Computing gradients on target convolutional layer' },
    { label: 'Metadata Header Inspection', icon: FileSearch, detail: 'Analyzing EXIF/ICC profile structures' },
    { label: 'Forensic Consistency Validation', icon: ShieldCheck, detail: 'Synthesizing evidence probabilities' },
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentStageIndex((prev) => (prev < stages.length - 1 ? prev + 1 : prev));
    }, 900);
    return () => clearInterval(timer);
  }, [stages.length]);

  return (
    <div className="cyber-card cyber-corners" style={{
      marginBottom: '28px',
      border: '1px solid var(--border-cyan-active)',
      boxShadow: 'var(--shadow-cyan-strong)',
      backgroundColor: 'rgba(10, 16, 30, 0.9)'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid var(--border-subtle)',
        paddingBottom: '16px',
        marginBottom: '24px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '6px',
            backgroundColor: 'rgba(0, 242, 254, 0.15)',
            border: '1px solid var(--border-cyan)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Activity size={18} color="var(--cyber-cyan)" />
          </div>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: 700, margin: 0 }}>
              Forensic Inference in Progress
            </h3>
            <span className="mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              TARGET: {filename} • ENGINE: EfficientNet-B0 (PORT 8000)
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="pulse-dot pulse-dot-cyan" />
          <span className="mono" style={{ fontSize: '12px', color: 'var(--cyber-cyan)', fontWeight: 600 }}>
            SCANNING MEDIA
          </span>
        </div>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'minmax(200px, 280px) 1fr',
        gap: '28px',
        alignItems: 'center'
      }}>
        {/* Scanning Laser Image Box */}
        <div style={{
          position: 'relative',
          height: '240px',
          borderRadius: '8px',
          overflow: 'hidden',
          border: '1px solid var(--border-cyan)',
          backgroundColor: '#000000',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          {previewUrl && (
            <img
              src={previewUrl}
              alt="Scanning Target"
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'contain',
                opacity: 0.8
              }}
            />
          )}

          {/* Laser beam */}
          <div className="scan-laser" />

          {/* Grid overlay */}
          <div style={{
            position: 'absolute',
            inset: 0,
            backgroundImage: 'linear-gradient(rgba(0, 242, 254, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 242, 254, 0.1) 1px, transparent 1px)',
            backgroundSize: '20px 20px',
            pointerEvents: 'none'
          }} />

          <div style={{
            position: 'absolute',
            bottom: '8px',
            left: '8px',
            right: '8px',
            backgroundColor: 'rgba(5, 8, 17, 0.85)',
            backdropFilter: 'blur(4px)',
            padding: '4px 8px',
            borderRadius: '4px',
            border: '1px solid var(--border-subtle)',
            fontSize: '10px',
            fontFamily: 'var(--font-mono)',
            color: 'var(--cyber-cyan)',
            display: 'flex',
            justifyContent: 'space-between'
          }}>
            <span>PIXEL GRID: 224x224</span>
            <span>CHANNELS: RGB</span>
          </div>
        </div>

        {/* Forensic Stage Telemetry */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {stages.map((stage, idx) => {
            const isCompleted = idx < currentStageIndex;
            const isCurrent = idx === currentStageIndex;
            const Icon = stage.icon;

            return (
              <div
                key={stage.label}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '14px',
                  padding: '10px 16px',
                  borderRadius: '8px',
                  backgroundColor: isCurrent ? 'rgba(0, 242, 254, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                  border: `1px solid ${isCurrent ? 'var(--border-cyan)' : isCompleted ? 'rgba(16, 185, 129, 0.3)' : 'var(--border-subtle)'}`,
                  transition: 'all 0.3s ease'
                }}
              >
                <div style={{
                  width: '28px',
                  height: '28px',
                  borderRadius: '6px',
                  backgroundColor: isCurrent ? 'rgba(0, 242, 254, 0.15)' : isCompleted ? 'rgba(16, 185, 129, 0.15)' : 'rgba(255, 255, 255, 0.05)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: isCurrent ? 'var(--cyber-cyan)' : isCompleted ? 'var(--status-real)' : 'var(--text-muted)'
                }}>
                  <Icon size={16} />
                </div>

                <div style={{ flex: 1 }}>
                  <div style={{
                    fontSize: '13px',
                    fontWeight: 600,
                    color: isCurrent ? 'var(--cyber-cyan)' : isCompleted ? 'var(--text-primary)' : 'var(--text-muted)'
                  }}>
                    {stage.label}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                    {stage.detail}
                  </div>
                </div>

                <div>
                  {isCompleted && (
                    <span className="badge badge-real" style={{ fontSize: '9px' }}>COMPLETE</span>
                  )}
                  {isCurrent && (
                    <span className="badge badge-cyan" style={{ fontSize: '9px' }}>PROCESSING</span>
                  )}
                  {!isCompleted && !isCurrent && (
                    <span className="badge badge-pending" style={{ fontSize: '9px' }}>QUEUED</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
