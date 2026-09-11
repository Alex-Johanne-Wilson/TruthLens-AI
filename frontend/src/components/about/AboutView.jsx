import React from 'react';
import { Info, Cpu, ShieldCheck, FileCheck, Layers, GitBranch, Terminal } from 'lucide-react';

export default function AboutView() {
  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ marginBottom: '28px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <Info size={18} color="var(--cyber-cyan)" />
          <span className="mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            SYSTEM ARCHITECTURE // MODEL CARD
          </span>
        </div>
        <h2 style={{ fontSize: '28px', fontWeight: 800, margin: 0 }}>
          About TruthLens & Model Architecture
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginTop: '4px' }}>
          Digital evidence authenticity analysis powered by deep convolutional feature extraction and explainable AI.
        </p>
      </div>

      {/* Model Card */}
      <div className="cyber-card" style={{ marginBottom: '24px' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid var(--border-subtle)',
          paddingBottom: '14px',
          marginBottom: '16px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Cpu size={18} color="var(--cyber-cyan)" />
            <h3 style={{ fontSize: '16px', fontWeight: 700, margin: 0 }}>
              AI Detector Model Card: EfficientNet-B0
            </h3>
          </div>
          <span className="badge badge-real">VERIFIED CHECKPOINT</span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px', marginBottom: '18px' }}>
          <div style={{ backgroundColor: 'rgba(5, 8, 17, 0.6)', padding: '12px', borderRadius: '6px' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Architecture</div>
            <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>EfficientNet-B0 PyTorch</div>
          </div>
          <div style={{ backgroundColor: 'rgba(5, 8, 17, 0.6)', padding: '12px', borderRadius: '6px' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Output Classes</div>
            <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--cyber-cyan)' }}>0: AI-Generated, 1: Real</div>
          </div>
          <div style={{ backgroundColor: 'rgba(5, 8, 17, 0.6)', padding: '12px', borderRadius: '6px' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Checkpoint Location</div>
            <div className="mono" style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>outputs/checkpoints/best_model.pth</div>
          </div>
        </div>

        <div style={{ backgroundColor: 'rgba(5, 8, 17, 0.8)', padding: '12px 16px', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>
            SHA-256 CHECKPOINT HASH (CRYPTOGRAPHIC INTEGRITY):
          </div>
          <div className="mono" style={{ fontSize: '11px', color: 'var(--cyber-cyan)', wordBreak: 'break-all' }}>
            123DB4AE74A00718F51023979D0F72BAA212E66CBF23AF32977B6D39CC2621B7
          </div>
        </div>
      </div>

      {/* Explainable AI & Grad-CAM */}
      <div className="cyber-card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
          <Layers size={18} color="var(--cyber-cyan)" />
          <h3 style={{ fontSize: '16px', fontWeight: 700, margin: 0 }}>
            Explainable AI: Gradient-Weighted Class Activation Mapping (Grad-CAM)
          </h3>
        </div>

        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          TruthLens employs Grad-CAM to ensure full transparency and auditability in judicial and investigative contexts. By calculating gradients of the predicted class score with respect to the final convolutional feature maps of EfficientNet-B0, TruthLens produces a coarse 2D localization map highlighting pixel regions that contributed most to the authenticity determination.
        </p>
      </div>

      {/* Forensic Pipeline Architecture Team */}
      <div className="cyber-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
          <GitBranch size={18} color="var(--cyber-cyan)" />
          <h3 style={{ fontSize: '16px', fontWeight: 700, margin: 0 }}>
            Forensic Team Roles & Architectural Modularization
          </h3>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div style={{ padding: '12px 14px', borderRadius: '6px', backgroundColor: 'rgba(5, 8, 17, 0.5)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontWeight: 600, color: 'var(--cyber-cyan)', fontSize: '13px' }}>Alex Wilson — AI Model Training & Inference API</div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>EfficientNet-B0 architecture, PyTorch training, Grad-CAM visualization pipeline, and FastAPI backend endpoints.</div>
          </div>

          <div style={{ padding: '12px 14px', borderRadius: '6px', backgroundColor: 'rgba(5, 8, 17, 0.5)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontWeight: 600, color: 'var(--cyber-purple)', fontSize: '13px' }}>Vidhi — Metadata & Container Forensics</div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>EXIF inspection, ICC profile verification, GPS geospatial consistency, and metadata anomaly detection.</div>
          </div>

          <div style={{ padding: '12px 14px', borderRadius: '6px', backgroundColor: 'rgba(5, 8, 17, 0.5)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontWeight: 600, color: 'var(--text-accent)', fontSize: '13px' }}>Alec — Classical Forensic Algorithms</div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Error Level Analysis (ELA), Copy-Move keypoint matching, DCT compression grid check, and PRNU noise variance.</div>
          </div>
        </div>
      </div>
    </div>
  );
}
