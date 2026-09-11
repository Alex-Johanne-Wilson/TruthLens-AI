import React, { useState, useEffect } from 'react';
import { History, Trash2, Search, Filter, ShieldCheck, AlertTriangle, FileText, Eye } from 'lucide-react';

export default function HistoryView({ onSelectEvidence }) {
  const [historyItems, setHistoryItems] = useState([]);
  const [filterText, setFilterText] = useState('');

  // Initial seed if localStorage is empty
  useEffect(() => {
    try {
      const stored = localStorage.getItem('truthlens_history');
      if (stored) {
        setHistoryItems(JSON.parse(stored));
      } else {
        const seed = [
          {
            id: 'SCAN-9021',
            filename: 'real_0001.jpg',
            analysisType: 'Image Forensics',
            verdict: 'real',
            confidence: 99.98,
            timestamp: '2026-09-11 09:38:37 UTC',
            status: 'Completed',
            gradcam_path: '/static/gradcam/gradcam_real_0001.png'
          },
          {
            id: 'SCAN-9020',
            filename: 'synthetic_portrait_gen.png',
            analysisType: 'Image Forensics',
            verdict: 'ai_generated',
            confidence: 99.85,
            timestamp: '2026-09-11 09:12:15 UTC',
            status: 'Completed',
            gradcam_path: null
          },
          {
            id: 'SCAN-9019',
            filename: 'interview_clip_4k.mp4',
            analysisType: 'Deepfake Prototype',
            verdict: 'untrained',
            confidence: 0,
            timestamp: '2026-09-11 08:45:00 UTC',
            status: 'Untrained Model',
            gradcam_path: null
          },
        ];
        localStorage.setItem('truthlens_history', JSON.stringify(seed));
        setHistoryItems(seed);
      }
    } catch (e) {
      console.error(e);
    }
  }, []);

  const handleClear = () => {
    localStorage.removeItem('truthlens_history');
    setHistoryItems([]);
  };

  const filtered = historyItems.filter((item) => 
    item.filename.toLowerCase().includes(filterText.toLowerCase()) ||
    item.verdict.toLowerCase().includes(filterText.toLowerCase()) ||
    item.analysisType.toLowerCase().includes(filterText.toLowerCase())
  );

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '28px',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <History size={18} color="var(--cyber-cyan)" />
            <span className="mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              EVIDENCE VAULT // HISTORICAL LOGS
            </span>
          </div>
          <h2 style={{ fontSize: '28px', fontWeight: 800, margin: 0 }}>
            Analysis History & Audit Vault
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '2px' }}>
            Historical record of analyzed digital media artifacts with persistent client audit trail.
          </p>
        </div>

        <button onClick={handleClear} className="btn-secondary" style={{ fontSize: '12px' }}>
          <Trash2 size={14} color="var(--status-ai)" />
          Clear Vault Logs
        </button>
      </div>

      {/* Filter / Search Bar */}
      <div className="cyber-card" style={{ padding: '14px 20px', marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Search size={16} color="var(--text-muted)" />
          <input
            type="text"
            placeholder="Filter by filename, verdict (real, ai_generated), or analysis type..."
            value={filterText}
            onChange={(e) => setFilterText(e.target.value)}
            style={{
              flex: 1,
              backgroundColor: 'transparent',
              border: 'none',
              outline: 'none',
              color: 'var(--text-primary)',
              fontSize: '13px',
              fontFamily: 'var(--font-sans)'
            }}
          />
        </div>
      </div>

      {/* Table */}
      <div className="cyber-card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
            <thead>
              <tr style={{
                backgroundColor: 'rgba(5, 8, 17, 0.6)',
                borderBottom: '1px solid var(--border-subtle)',
                color: 'var(--text-muted)',
                fontSize: '11px',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}>
                <th style={{ padding: '14px 20px' }}>Evidence ID</th>
                <th style={{ padding: '14px 20px' }}>Filename</th>
                <th style={{ padding: '14px 20px' }}>Type</th>
                <th style={{ padding: '14px 20px' }}>Verdict</th>
                <th style={{ padding: '14px 20px' }}>Confidence</th>
                <th style={{ padding: '14px 20px' }}>Timestamp</th>
                <th style={{ padding: '14px 20px' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ padding: '36px', textAlign: 'center', color: 'var(--text-muted)' }}>
                    No analysis history records match your search query.
                  </td>
                </tr>
              ) : (
                filtered.map((item) => {
                  const isReal = item.verdict === 'real';
                  const isAI = item.verdict === 'ai_generated';

                  return (
                    <tr
                      key={item.id}
                      style={{
                        borderBottom: '1px solid var(--border-subtle)',
                        transition: 'background-color 0.15s ease'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.02)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = 'transparent';
                      }}
                    >
                      <td className="mono" style={{ padding: '14px 20px', color: 'var(--cyber-cyan)', fontWeight: 600 }}>
                        {item.id}
                      </td>
                      <td style={{ padding: '14px 20px', color: 'var(--text-primary)', fontWeight: 600 }}>
                        {item.filename}
                      </td>
                      <td style={{ padding: '14px 20px', color: 'var(--text-secondary)' }}>
                        {item.analysisType}
                      </td>
                      <td style={{ padding: '14px 20px' }}>
                        {isReal && (
                          <span className="badge badge-real">
                            <ShieldCheck size={12} /> REAL
                          </span>
                        )}
                        {isAI && (
                          <span className="badge badge-ai">
                            <AlertTriangle size={12} /> AI-GENERATED
                          </span>
                        )}
                        {!isReal && !isAI && (
                          <span className="badge badge-pending">
                            {item.verdict.toUpperCase()}
                          </span>
                        )}
                      </td>
                      <td className="mono" style={{ padding: '14px 20px', fontWeight: 600 }}>
                        {item.confidence > 0 ? `${item.confidence}%` : 'N/A'}
                      </td>
                      <td className="mono" style={{ padding: '14px 20px', color: 'var(--text-muted)', fontSize: '11px' }}>
                        {item.timestamp}
                      </td>
                      <td style={{ padding: '14px 20px' }}>
                        <span className="badge badge-cyan" style={{ fontSize: '9px' }}>
                          {item.status}
                        </span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
