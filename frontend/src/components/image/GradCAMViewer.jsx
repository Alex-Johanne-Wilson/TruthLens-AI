import React, { useState } from 'react';
import { Layers, Maximize2, Minimize2, Eye, HelpCircle, Download } from 'lucide-react';
import { resolveGradcamUrl } from '../../services/api';

export default function GradCAMViewer({ originalUrl, gradcamPath, filename }) {
  const [viewMode, setViewMode] = useState('side-by-side'); // 'side-by-side' | 'heatmap' | 'original'
  const [isFullscreen, setIsFullscreen] = useState(false);

  const fullGradcamUrl = resolveGradcamUrl(gradcamPath);

  return (
    <div className="cyber-card cyber-corners" style={{ marginBottom: '28px' }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid var(--border-subtle)',
        paddingBottom: '16px',
        marginBottom: '20px',
        flexWrap: 'wrap',
        gap: '12px'
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
            <Layers size={18} color="var(--cyber-cyan)" />
          </div>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: 700, margin: 0 }}>
              Grad-CAM Visualization
            </h3>
            <span className="mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              EXPLAINABLE AI HEATMAP • BACKWARD CONVOLUTION ACTIVATION
            </span>
          </div>
        </div>

        {/* View mode toggle controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            display: 'inline-flex',
            backgroundColor: 'rgba(5, 8, 17, 0.8)',
            padding: '3px',
            borderRadius: '8px',
            border: '1px solid var(--border-subtle)'
          }}>
            <button
              onClick={() => setViewMode('side-by-side')}
              style={{
                background: viewMode === 'side-by-side' ? 'rgba(0, 242, 254, 0.15)' : 'transparent',
                color: viewMode === 'side-by-side' ? 'var(--cyber-cyan)' : 'var(--text-muted)',
                border: viewMode === 'side-by-side' ? '1px solid var(--border-cyan)' : '1px solid transparent',
                borderRadius: '6px',
                padding: '4px 10px',
                fontSize: '11px',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              Side-by-Side
            </button>
            <button
              onClick={() => setViewMode('heatmap')}
              style={{
                background: viewMode === 'heatmap' ? 'rgba(0, 242, 254, 0.15)' : 'transparent',
                color: viewMode === 'heatmap' ? 'var(--cyber-cyan)' : 'var(--text-muted)',
                border: viewMode === 'heatmap' ? '1px solid var(--border-cyan)' : '1px solid transparent',
                borderRadius: '6px',
                padding: '4px 10px',
                fontSize: '11px',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              Heatmap Only
            </button>
            <button
              onClick={() => setViewMode('original')}
              style={{
                background: viewMode === 'original' ? 'rgba(0, 242, 254, 0.15)' : 'transparent',
                color: viewMode === 'original' ? 'var(--cyber-cyan)' : 'var(--text-muted)',
                border: viewMode === 'original' ? '1px solid var(--border-cyan)' : '1px solid transparent',
                borderRadius: '6px',
                padding: '4px 10px',
                fontSize: '11px',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              Original Only
            </button>
          </div>

          <button
            onClick={() => setIsFullscreen(true)}
            className="btn-ghost"
            style={{ padding: '6px 10px' }}
            title="Inspect Fullscreen"
          >
            <Maximize2 size={16} />
          </button>
        </div>
      </div>

      {/* Explanation Banner */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        padding: '10px 14px',
        borderRadius: '8px',
        backgroundColor: 'rgba(0, 242, 254, 0.05)',
        border: '1px solid rgba(0, 242, 254, 0.15)',
        marginBottom: '20px',
        fontSize: '12px',
        color: 'var(--text-secondary)'
      }}>
        <HelpCircle size={16} color="var(--cyber-cyan)" style={{ flexShrink: 0 }} />
        <span>
          <strong style={{ color: 'var(--cyber-cyan)' }}>Forensic Interpretability:</strong> Highlighted regions show the areas that most influenced the model’s decision. Red and yellow regions indicate high convolutional feature sensitivity.
        </span>
      </div>

      {/* Image Display Container */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: viewMode === 'side-by-side' ? 'repeat(auto-fit, minmax(280px, 1fr))' : '1fr',
        gap: '20px'
      }}>
        {/* Original Image */}
        {(viewMode === 'side-by-side' || viewMode === 'original') && (
          <div style={{
            backgroundColor: '#000000',
            borderRadius: '8px',
            overflow: 'hidden',
            border: '1px solid var(--border-subtle)',
            position: 'relative'
          }}>
            <div style={{
              position: 'absolute',
              top: '12px',
              left: '12px',
              backgroundColor: 'rgba(5, 8, 17, 0.8)',
              backdropFilter: 'blur(6px)',
              padding: '4px 10px',
              borderRadius: '4px',
              border: '1px solid var(--border-subtle)',
              fontSize: '11px',
              fontWeight: 600,
              color: 'var(--text-secondary)',
              zIndex: 2
            }}>
              Original Evidence
            </div>

            <div style={{
              height: '340px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: 'rgba(0, 0, 0, 0.6)'
            }}>
              <img
                src={originalUrl}
                alt="Original Evidence"
                style={{
                  maxWidth: '100%',
                  maxHeight: '100%',
                  objectFit: 'contain'
                }}
              />
            </div>
          </div>
        )}

        {/* Grad-CAM Heatmap Image */}
        {(viewMode === 'side-by-side' || viewMode === 'heatmap') && (
          <div style={{
            backgroundColor: '#000000',
            borderRadius: '8px',
            overflow: 'hidden',
            border: '1px solid var(--border-cyan)',
            position: 'relative',
            boxShadow: 'var(--shadow-cyan)'
          }}>
            <div style={{
              position: 'absolute',
              top: '12px',
              left: '12px',
              backgroundColor: 'rgba(5, 8, 17, 0.85)',
              backdropFilter: 'blur(6px)',
              padding: '4px 10px',
              borderRadius: '4px',
              border: '1px solid var(--border-cyan)',
              fontSize: '11px',
              fontWeight: 700,
              color: 'var(--cyber-cyan)',
              zIndex: 2,
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <Eye size={12} />
              Grad-CAM Activation Heatmap
            </div>

            <div style={{
              height: '340px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: 'rgba(0, 0, 0, 0.8)'
            }}>
              {fullGradcamUrl ? (
                <img
                  src={fullGradcamUrl}
                  alt="Grad-CAM Forensic Overlay"
                  style={{
                    maxWidth: '100%',
                    maxHeight: '100%',
                    objectFit: 'contain'
                  }}
                  onError={(e) => {
                    console.error('Failed loading Grad-CAM from', fullGradcamUrl);
                  }}
                />
              ) : (
                <div style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
                  No Grad-CAM output available
                </div>
              )}
            </div>

            {/* Static serving path badge */}
            <div style={{
              position: 'absolute',
              bottom: '10px',
              right: '12px',
              backgroundColor: 'rgba(5, 8, 17, 0.8)',
              padding: '3px 8px',
              borderRadius: '4px',
              fontSize: '10px',
              color: 'var(--text-muted)',
              fontFamily: 'var(--font-mono)'
            }}>
              {gradcamPath}
            </div>
          </div>
        )}
      </div>

      {/* Fullscreen Modal Dialog */}
      {isFullscreen && (
        <div className="modal-backdrop" onClick={() => setIsFullscreen(false)}>
          <div 
            className="cyber-card"
            onClick={(e) => e.stopPropagation()}
            style={{
              maxWidth: '90vw',
              maxHeight: '90vh',
              width: '900px',
              display: 'flex',
              flexDirection: 'column',
              padding: '24px',
              border: '1px solid var(--border-cyan-active)',
              boxShadow: 'var(--shadow-cyan-strong)'
            }}
          >
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '16px'
            }}>
              <h3 style={{ fontSize: '18px', margin: 0 }}>
                High-Resolution Pixel & Grad-CAM Inspection
              </h3>
              <button onClick={() => setIsFullscreen(false)} className="btn-ghost">
                <Minimize2 size={18} />
              </button>
            </div>

            <div style={{
              height: '560px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: '#000000',
              borderRadius: '8px',
              overflow: 'hidden'
            }}>
              <img
                src={fullGradcamUrl || originalUrl}
                alt="High-Res Evidence Inspection"
                style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
