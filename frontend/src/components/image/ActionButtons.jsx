import React, { useState } from 'react';
import { Download, FileText, Share2, Check, Clock } from 'lucide-react';

export default function ActionButtons({ onViewFullReport, hasResult }) {
  const [copied, setCopied] = useState(false);

  const handleShare = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="cyber-card" style={{
      marginBottom: '28px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      flexWrap: 'wrap',
      gap: '16px'
    }}>
      <div>
        <h4 style={{ fontSize: '15px', fontWeight: 700, margin: 0 }}>
          Forensic Investigation Actions
        </h4>
        <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>
          Export evidence artifacts or transition to official digital dossier
        </p>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
        {/* View Full Report button */}
        <button
          onClick={onViewFullReport}
          disabled={!hasResult}
          className="btn-primary"
          style={{ fontSize: '13px', padding: '10px 18px' }}
        >
          <FileText size={16} />
          View Full Forensic Report
        </button>

        {/* Download PDF button (marked pending backend) */}
        <button
          disabled={true}
          className="btn-secondary"
          title="PDF generation backend module pending integration"
          style={{
            fontSize: '13px',
            padding: '10px 18px',
            opacity: 0.6,
            cursor: 'not-allowed'
          }}
        >
          <Download size={15} />
          Download Report (PDF) [Pending]
        </button>

        {/* Share Button */}
        <button
          onClick={handleShare}
          className="btn-secondary"
          style={{ fontSize: '13px', padding: '10px 16px' }}
          title="Copy Case URL"
        >
          {copied ? (
            <>
              <Check size={15} color="var(--status-real)" />
              Copied Link!
            </>
          ) : (
            <>
              <Share2 size={15} />
              Share Case
            </>
          )}
        </button>
      </div>
    </div>
  );
}
