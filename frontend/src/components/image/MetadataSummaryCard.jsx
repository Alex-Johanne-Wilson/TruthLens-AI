import React from 'react';
import { FileSearch, Camera, Calendar, MapPin, Code2, AlertCircle, Clock } from 'lucide-react';

export default function MetadataSummaryCard() {
  const metadataFields = [
    { label: 'Camera / Device Model', icon: Camera, status: 'Pending integration', note: 'EXIF Make & Model tags' },
    { label: 'Original Capture Date', icon: Calendar, status: 'Pending integration', note: 'DateTimeOriginal / Digitized' },
    { label: 'Geospatial GPS Coordinates', icon: MapPin, status: 'Pending integration', note: 'GPSLatitude / GPSLongitude' },
    { label: 'Encoding Software / Firmware', icon: Code2, status: 'Pending integration', note: 'Software signature verification' },
    { label: 'Metadata Consistency Score', icon: AlertCircle, status: 'Pending integration', note: 'Timestamp & container coherence' },
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
            backgroundColor: 'rgba(139, 92, 246, 0.15)',
            border: '1px solid rgba(139, 92, 246, 0.3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <FileSearch size={18} color="var(--cyber-purple)" />
          </div>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: 700, margin: 0 }}>
              Metadata Summary
            </h3>
            <span className="mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              EXIF & CONTAINER INTEGRITY MODULE // VIDHI HOOK
            </span>
          </div>
        </div>

        <span className="badge badge-pending" style={{ fontSize: '9px' }}>
          MODULE PENDING INTEGRATION
        </span>
      </div>

      {/* Honest pending integration notice */}
      <div style={{
        backgroundColor: 'rgba(5, 8, 17, 0.45)',
        border: '1px dashed var(--border-glass)',
        borderRadius: '8px',
        padding: '16px 20px',
        marginBottom: '16px',
        display: 'flex',
        alignItems: 'center',
        gap: '12px'
      }}>
        <Clock size={18} color="var(--text-muted)" style={{ flexShrink: 0 }} />
        <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
          <strong style={{ color: 'var(--text-primary)' }}>Metadata Analysis Pending:</strong> The metadata extraction backend module is currently undergoing staging. The fields below reflect the schema structured for Vidhi's metadata engine.
        </div>
      </div>

      {/* Field placeholders */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '12px'
      }}>
        {metadataFields.map((field) => {
          const Icon = field.icon;
          return (
            <div
              key={field.label}
              style={{
                backgroundColor: 'rgba(255, 255, 255, 0.02)',
                padding: '12px 14px',
                borderRadius: '8px',
                border: '1px solid var(--border-subtle)',
                display: 'flex',
                flexDirection: 'column',
                gap: '4px'
              }}
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                fontSize: '11px',
                color: 'var(--text-muted)'
              }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Icon size={12} color="var(--cyber-purple)" />
                  {field.label}
                </span>
              </div>

              <div className="mono" style={{
                fontSize: '12px',
                color: 'var(--text-muted)',
                fontStyle: 'italic',
                marginTop: '2px'
              }}>
                [Awaiting Metadata API]
              </div>

              <div style={{ fontSize: '10px', color: 'rgba(148, 163, 184, 0.6)' }}>
                {field.note}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
