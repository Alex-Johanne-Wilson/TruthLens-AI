import React from 'react';
import { Upload, Scan, Cpu, ShieldCheck, FileCheck, Check } from 'lucide-react';

export default function WorkflowStepper({ currentStep }) {
  // Steps: 'upload' (1), 'scanning' (2), 'ai-analysis' (3), 'forensics' (4), 'report' (5)
  const steps = [
    { id: 'upload', number: 1, label: 'Upload Evidence', icon: Upload },
    { id: 'scanning', number: 2, label: 'Scanning', icon: Scan },
    { id: 'ai-analysis', number: 3, label: 'AI Analysis', icon: Cpu },
    { id: 'forensics', number: 4, label: 'Forensic Checks', icon: ShieldCheck },
    { id: 'report', number: 5, label: 'Forensic Report', icon: FileCheck },
  ];

  const getStepStatus = (index) => {
    const stepOrder = ['upload', 'scanning', 'ai-analysis', 'forensics', 'report'];
    const currentIndex = stepOrder.indexOf(currentStep);
    if (currentIndex > index) return 'completed';
    if (currentIndex === index) return 'active';
    return 'pending';
  };

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '14px 24px',
      backgroundColor: 'rgba(13, 20, 36, 0.6)',
      border: '1px solid var(--border-subtle)',
      borderRadius: '12px',
      marginBottom: '28px',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Subtle background track line */}
      <div style={{
        position: 'absolute',
        top: '50%',
        left: '60px',
        right: '60px',
        height: '2px',
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        transform: 'translateY(-50%)',
        zIndex: 1
      }} />

      {steps.map((step, idx) => {
        const status = getStepStatus(idx);
        const Icon = step.icon;

        let iconBg = 'rgba(15, 23, 42, 0.9)';
        let iconBorder = 'var(--border-subtle)';
        let iconColor = 'var(--text-muted)';
        let textColor = 'var(--text-muted)';
        let glow = 'none';

        if (status === 'completed') {
          iconBg = 'rgba(16, 185, 129, 0.15)';
          iconBorder = 'var(--status-real)';
          iconColor = 'var(--status-real)';
          textColor = 'var(--text-primary)';
          glow = 'var(--shadow-real)';
        } else if (status === 'active') {
          iconBg = 'rgba(0, 242, 254, 0.15)';
          iconBorder = 'var(--cyber-cyan)';
          iconColor = 'var(--cyber-cyan)';
          textColor = 'var(--cyber-cyan)';
          glow = 'var(--shadow-cyan)';
        }

        return (
          <div 
            key={step.id} 
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              position: 'relative',
              zIndex: 2,
              backgroundColor: 'var(--bg-card-solid)',
              padding: '6px 14px',
              borderRadius: '9999px',
              border: `1px solid ${iconBorder}`,
              boxShadow: glow,
              transition: 'all 0.3s ease'
            }}
          >
            <div style={{
              width: '24px',
              height: '24px',
              borderRadius: '50%',
              backgroundColor: iconBg,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: iconColor,
              fontSize: '11px',
              fontWeight: 700
            }}>
              {status === 'completed' ? (
                <Check size={14} color="var(--status-real)" />
              ) : (
                <Icon size={13} color={iconColor} />
              )}
            </div>

            <div style={{
              fontSize: '12px',
              fontWeight: status === 'active' ? 700 : 500,
              color: textColor,
              letterSpacing: '0.02em',
              whiteSpace: 'nowrap'
            }}>
              {step.label}
            </div>
          </div>
        );
      })}
    </div>
  );
}
