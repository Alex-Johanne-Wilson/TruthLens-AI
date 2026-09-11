import React from 'react';
import { ShieldCheck, AlertTriangle, CheckCircle, Percent, Cpu, Activity } from 'lucide-react';

export default function ResultCard({ result }) {
  if (!result) return null;

  const isReal = result.predicted_class?.toLowerCase() === 'real';
  const confidencePercent = (result.confidence * 100).toFixed(2);
  const realProbPercent = (result.real_probability * 100).toFixed(2);
  const aiProbPercent = (result.ai_probability * 100).toFixed(2);

  // Verification sum
  const probSum = (result.real_probability + result.ai_probability).toFixed(4);

  return (
    <div 
      className="cyber-card cyber-corners"
      style={{
        marginBottom: '28px',
        border: `1px solid ${isReal ? 'var(--status-real-border)' : 'var(--status-ai-border)'}`,
        boxShadow: isReal ? 'var(--shadow-real)' : 'var(--shadow-ai)',
        backgroundColor: isReal ? 'rgba(10, 26, 20, 0.75)' : 'rgba(28, 12, 16, 0.75)'
      }}
    >
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid var(--border-subtle)',
        paddingBottom: '16px',
        marginBottom: '20px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            EVIDENCE VERDICT // CLASSIFICATION ENGINE
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className={`badge ${isReal ? 'badge-real' : 'badge-ai'}`}>
            INFERENCE VERIFIED
          </span>
        </div>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'minmax(280px, 1.2fr) minmax(280px, 1fr)',
        gap: '32px',
        alignItems: 'center'
      }}>
        {/* Left: Verdict Banner */}
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '20px' }}>
          <div style={{
            width: '64px',
            height: '64px',
            borderRadius: '12px',
            backgroundColor: isReal ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
            border: `1px solid ${isReal ? 'var(--status-real)' : 'var(--status-ai)'}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: isReal ? '0 0 20px rgba(16, 185, 129, 0.3)' : '0 0 20px rgba(239, 68, 68, 0.3)',
            flexShrink: 0
          }}>
            {isReal ? (
              <ShieldCheck size={36} color="var(--status-real)" />
            ) : (
              <AlertTriangle size={36} color="var(--status-ai)" />
            )}
          </div>

          <div>
            <div style={{
              fontSize: '11px',
              fontWeight: 700,
              letterSpacing: '0.08em',
              color: isReal ? 'var(--status-real)' : 'var(--status-ai)',
              textTransform: 'uppercase',
              marginBottom: '4px'
            }}>
              Forensic Verdict
            </div>

            <div style={{
              fontSize: '32px',
              fontWeight: 800,
              fontFamily: 'var(--font-heading)',
              color: isReal ? 'var(--status-real)' : 'var(--status-ai)',
              letterSpacing: '-0.02em',
              lineHeight: 1.1
            }}>
              {isReal ? 'REAL' : 'AI-GENERATED'}
            </div>

            <div style={{
              fontSize: '14px',
              color: 'var(--text-secondary)',
              marginTop: '8px',
              maxWidth: '380px'
            }}>
              {isReal 
                ? 'This image appears to be real and exhibits natural sensor and frequency distribution patterns.'
                : 'This image shows characteristics and latent artifacts associated with AI-generated synthetic content.'
              }
            </div>

            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              marginTop: '12px',
              padding: '4px 10px',
              borderRadius: '6px',
              backgroundColor: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid var(--border-subtle)',
              fontSize: '12px'
            }}>
              <Percent size={13} color="var(--cyber-cyan)" />
              <span style={{ color: 'var(--text-muted)' }}>Confidence: </span>
              <span className="mono" style={{ color: 'var(--text-primary)', fontWeight: 700 }}>
                {confidencePercent}%
              </span>
            </div>
          </div>
        </div>

        {/* Right: Probability Progress Bars */}
        <div style={{
          backgroundColor: 'rgba(5, 8, 17, 0.5)',
          padding: '20px',
          borderRadius: '10px',
          border: '1px solid var(--border-subtle)',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '12px',
            color: 'var(--text-muted)'
          }}>
            <span style={{ fontWeight: 600 }}>PROBABILITY DISTRIBUTION</span>
            <span className="mono" style={{ fontSize: '11px', color: 'var(--cyber-cyan)' }}>
              SUM: {probSum} ≈ 1.00
            </span>
          </div>

          {/* Real Probability Bar */}
          <div>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontSize: '13px',
              fontWeight: 600,
              marginBottom: '6px'
            }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--status-real)' }}>
                <CheckCircle size={14} />
                Real Probability
              </span>
              <span className="mono" style={{ color: 'var(--text-primary)', fontWeight: 700 }}>
                {realProbPercent}%
              </span>
            </div>
            <div style={{
              width: '100%',
              height: '8px',
              backgroundColor: 'rgba(255, 255, 255, 0.06)',
              borderRadius: '4px',
              overflow: 'hidden',
              position: 'relative'
            }}>
              <div style={{
                width: `${realProbPercent}%`,
                height: '100%',
                backgroundColor: 'var(--status-real)',
                borderRadius: '4px',
                boxShadow: '0 0 10px var(--status-real)',
                transition: 'width 0.8s cubic-bezier(0.4, 0, 0.2, 1)'
              }} />
            </div>
          </div>

          {/* AI Probability Bar */}
          <div>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontSize: '13px',
              fontWeight: 600,
              marginBottom: '6px'
            }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--status-ai)' }}>
                <AlertTriangle size={14} />
                AI-Generated Probability
              </span>
              <span className="mono" style={{ color: 'var(--text-primary)', fontWeight: 700 }}>
                {aiProbPercent}%
              </span>
            </div>
            <div style={{
              width: '100%',
              height: '8px',
              backgroundColor: 'rgba(255, 255, 255, 0.06)',
              borderRadius: '4px',
              overflow: 'hidden',
              position: 'relative'
            }}>
              <div style={{
                width: `${aiProbPercent}%`,
                height: '100%',
                backgroundColor: 'var(--status-ai)',
                borderRadius: '4px',
                boxShadow: '0 0 10px var(--status-ai)',
                transition: 'width 0.8s cubic-bezier(0.4, 0, 0.2, 1)'
              }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
