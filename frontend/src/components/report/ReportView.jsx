import React from 'react';
import { 
  FileText, 
  ShieldCheck, 
  AlertTriangle, 
  Printer, 
  Download, 
  Layers, 
  FileSearch, 
  Lock,
  Cpu,
  Clock,
  HardDrive,
  Award
} from 'lucide-react';
import { resolveGradcamUrl } from '../../services/api';

export default function ReportView({ currentEvidence, lastResult, previewUrl }) {
  const isReal = lastResult?.predicted_class?.toLowerCase() === 'real';
  const confidencePercent = lastResult ? (lastResult.confidence * 100).toFixed(2) : '99.98';
  const realProb = lastResult ? (lastResult.real_probability * 100).toFixed(2) : '99.98';
  const aiProb = lastResult ? (lastResult.ai_probability * 100).toFixed(2) : '0.00';
  const gradcamUrl = resolveGradcamUrl(lastResult?.gradcam_path);

  const evidenceId = 'TL-EV-2026-091184';
  const dateString = new Date().toUTCString();

  return (
    <div style={{ maxWidth: '960px', margin: '0 auto' }}>
      {/* Top action bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '24px',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileText size={18} color="var(--cyber-cyan)" />
            <span className="mono" style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              OFFICIAL DIGITAL FORENSIC DOSSIER
            </span>
          </div>
          <h2 style={{ fontSize: '24px', fontWeight: 800, margin: '2px 0 0 0' }}>
            Forensic Evidence Report
          </h2>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button
            onClick={() => window.print()}
            className="btn-secondary"
            style={{ fontSize: '13px', padding: '8px 16px' }}
          >
            <Printer size={15} />
            Print Dossier
          </button>

          <button
            disabled={true}
            className="btn-primary"
            style={{ fontSize: '13px', padding: '8px 18px', opacity: 0.6, cursor: 'not-allowed' }}
            title="Automated PDF compiling engine pending integration"
          >
            <Download size={15} />
            Download Report (PDF) [Pending]
          </button>
        </div>
      </div>

      {/* Formal Evidence Document Sheet */}
      <div 
        className="cyber-card"
        style={{
          backgroundColor: 'rgba(10, 16, 30, 0.95)',
          border: '1px solid var(--border-cyan)',
          padding: '40px',
          boxShadow: 'var(--shadow-lg)',
          borderRadius: '12px'
        }}
      >
        {/* Document Letterhead */}
        <div style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          borderBottom: '2px solid var(--border-cyan)',
          paddingBottom: '24px',
          marginBottom: '28px'
        }}>
          <div>
            <div style={{
              fontFamily: 'var(--font-heading)',
              fontSize: '26px',
              fontWeight: 800,
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              letterSpacing: '-0.02em'
            }}>
              <span>Truth</span>
              <span className="text-gradient-cyan">Lens</span>
              <span style={{ fontSize: '14px', color: 'var(--text-muted)', fontWeight: 500 }}>
                // DIGITAL FORENSICS LAB
              </span>
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
              Digital Evidence Authenticity & Machine Learning Verification Division
            </div>
          </div>

          <div style={{ textAlign: 'right' }}>
            <div className="mono" style={{ fontSize: '13px', fontWeight: 700, color: 'var(--cyber-cyan)' }}>
              {evidenceId}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
              DATE GENERATED: {dateString}
            </div>
            <div className="badge badge-cyan" style={{ marginTop: '6px', fontSize: '9px' }}>
              CLEARANCE: UNRESTRICTED FORENSIC
            </div>
          </div>
        </div>

        {/* Executive Verdict Callout */}
        <div style={{
          padding: '24px',
          borderRadius: '8px',
          backgroundColor: isReal ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.08)',
          border: `1px solid ${isReal ? 'var(--status-real-border)' : 'var(--status-ai-border)'}`,
          marginBottom: '28px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '16px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            {isReal ? (
              <ShieldCheck size={42} color="var(--status-real)" />
            ) : (
              <AlertTriangle size={42} color="var(--status-ai)" />
            )}
            <div>
              <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                PRIMARY FORENSIC VERDICT
              </div>
              <div style={{
                fontSize: '28px',
                fontWeight: 800,
                color: isReal ? 'var(--status-real)' : 'var(--status-ai)',
                letterSpacing: '-0.01em'
              }}>
                {isReal ? 'AUTHENTIC / REAL' : 'AI-GENERATED SYNTHETIC'}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                {isReal 
                  ? 'Exhibits expected physical camera noise and frequency consistency.' 
                  : 'Displays convolutional and semantic signatures characteristic of generative diffusion or GAN models.'}
              </div>
            </div>
          </div>

          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>STATISTICAL CONFIDENCE</div>
            <div className="mono" style={{ fontSize: '28px', fontWeight: 800, color: 'var(--text-primary)' }}>
              {confidencePercent}%
            </div>
            <div className="mono" style={{ fontSize: '11px', color: 'var(--cyber-cyan)' }}>
              Real: {realProb}% • AI: {aiProb}%
            </div>
          </div>
        </div>

        {/* Section 1: Target File Information */}
        <div style={{ marginBottom: '28px' }}>
          <h4 style={{
            fontSize: '14px',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            color: 'var(--cyber-cyan)',
            borderBottom: '1px solid var(--border-subtle)',
            paddingBottom: '8px',
            marginBottom: '14px'
          }}>
            1. Target Evidence Identification
          </h4>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '12px',
            fontSize: '12px'
          }}>
            <div style={{ backgroundColor: 'rgba(5, 8, 17, 0.5)', padding: '10px 14px', borderRadius: '6px' }}>
              <span style={{ color: 'var(--text-muted)' }}>File Identifier: </span>
              <span className="mono" style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
                {currentEvidence?.name || 'real_0001.jpg'}
              </span>
            </div>
            <div style={{ backgroundColor: 'rgba(5, 8, 17, 0.5)', padding: '10px 14px', borderRadius: '6px' }}>
              <span style={{ color: 'var(--text-muted)' }}>Engine Version: </span>
              <span className="mono" style={{ color: 'var(--cyber-cyan)' }}>
                EfficientNet-B0 (PyTorch)
              </span>
            </div>
            <div style={{ backgroundColor: 'rgba(5, 8, 17, 0.5)', padding: '10px 14px', borderRadius: '6px' }}>
              <span style={{ color: 'var(--text-muted)' }}>Inspection Protocol: </span>
              <span className="mono" style={{ color: 'var(--text-primary)' }}>
                Grad-CAM Activation v1
              </span>
            </div>
          </div>
        </div>

        {/* Section 2: Visual Explainability Artifacts */}
        <div style={{ marginBottom: '28px' }}>
          <h4 style={{
            fontSize: '14px',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            color: 'var(--cyber-cyan)',
            borderBottom: '1px solid var(--border-subtle)',
            paddingBottom: '8px',
            marginBottom: '14px'
          }}>
            2. Explainable Visual Evidence (Grad-CAM)
          </h4>

          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '16px'
          }}>
            <div style={{
              backgroundColor: '#000000',
              borderRadius: '8px',
              padding: '12px',
              border: '1px solid var(--border-subtle)',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '8px' }}>
                EXAMINED IMAGE ARTIFACT
              </div>
              <div style={{ height: '220px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <img
                  src={previewUrl || gradcamUrl}
                  alt="Original Artifact"
                  style={{ maxHeight: '100%', maxWidth: '100%', objectFit: 'contain' }}
                />
              </div>
            </div>

            <div style={{
              backgroundColor: '#000000',
              borderRadius: '8px',
              padding: '12px',
              border: '1px solid var(--border-cyan)',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '11px', color: 'var(--cyber-cyan)', marginBottom: '8px', fontWeight: 600 }}>
                GRAD-CAM SALIENCY HEATMAP
              </div>
              <div style={{ height: '220px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {gradcamUrl ? (
                  <img
                    src={gradcamUrl}
                    alt="Grad-CAM Output"
                    style={{ maxHeight: '100%', maxWidth: '100%', objectFit: 'contain' }}
                  />
                ) : (
                  <div style={{ color: 'var(--text-muted)', fontSize: '12px' }}>
                    Grad-CAM activation pending execution
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Section 3: Status of Sub-Modules */}
        <div style={{ marginBottom: '28px' }}>
          <h4 style={{
            fontSize: '14px',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            color: 'var(--cyber-cyan)',
            borderBottom: '1px solid var(--border-subtle)',
            paddingBottom: '8px',
            marginBottom: '14px'
          }}>
            3. Auxiliary Forensic Pipeline Status
          </h4>

          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)' }}>
                <th style={{ textAlign: 'left', padding: '8px 12px' }}>Forensic Sub-Module</th>
                <th style={{ textAlign: 'left', padding: '8px 12px' }}>Integration Phase</th>
                <th style={{ textAlign: 'left', padding: '8px 12px' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                <td style={{ padding: '8px 12px', color: 'var(--text-primary)' }}>AI Deep Convolutional Classifier</td>
                <td style={{ padding: '8px 12px', color: 'var(--text-secondary)' }}>Production Backend (FastAPI / PyTorch)</td>
                <td style={{ padding: '8px 12px' }}><span className="badge badge-real">Online</span></td>
              </tr>
              <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                <td style={{ padding: '8px 12px', color: 'var(--text-primary)' }}>EXIF & Metadata Header Validator</td>
                <td style={{ padding: '8px 12px', color: 'var(--text-secondary)' }}>Vidhi Pipeline Staging</td>
                <td style={{ padding: '8px 12px' }}><span className="badge badge-pending">Pending</span></td>
              </tr>
              <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                <td style={{ padding: '8px 12px', color: 'var(--text-primary)' }}>Classical Forensics (ELA / Copy-Move)</td>
                <td style={{ padding: '8px 12px', color: 'var(--text-secondary)' }}>Alec Pipeline Staging</td>
                <td style={{ padding: '8px 12px' }}><span className="badge badge-pending">Pending</span></td>
              </tr>
              <tr>
                <td style={{ padding: '8px 12px', color: 'var(--text-primary)' }}>Deepfake Video Biometrics</td>
                <td style={{ padding: '8px 12px', color: 'var(--text-secondary)' }}>Prototype Architecture</td>
                <td style={{ padding: '8px 12px' }}><span className="badge badge-ai">Prototype</span></td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Section 4: Forensic Disclaimer */}
        <div style={{
          padding: '16px',
          borderRadius: '8px',
          backgroundColor: 'rgba(5, 8, 17, 0.6)',
          border: '1px solid var(--border-subtle)',
          fontSize: '11px',
          color: 'var(--text-muted)',
          lineHeight: 1.5
        }}>
          <strong style={{ color: 'var(--text-secondary)' }}>Legal Forensic Disclaimer:</strong> This digital evidence report is generated by the TruthLens Automated Forensic Suite. Results represent statistical inference probabilities computed by deep convolutional neural networks and explainable gradient activation maps. This document is intended to assist digital evidence investigators and does not constitute a sole determination of authenticity without corroborating chain-of-custody verification.
        </div>
      </div>
    </div>
  );
}
