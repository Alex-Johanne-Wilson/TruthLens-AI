import React from 'react';
import { FileSearch, Camera, MapPin, Calendar, HardDrive, ShieldCheck, Clock, Layers } from 'lucide-react';

export default function MetadataView() {
  const metadataBlocks = [
    {
      title: 'EXIF Hardware Signatures',
      icon: Camera,
      fields: [
        { key: 'Camera Make', value: 'Pending Module Integration (Vidhi)' },
        { key: 'Camera Model', value: 'Pending Module Integration' },
        { key: 'Lens Specification', value: 'Pending Module Integration' },
        { key: 'Focal Length / Aperture', value: 'Pending Module Integration' },
        { key: 'ISO Sensitivity', value: 'Pending Module Integration' },
      ]
    },
    {
      title: 'Geospatial & Temporal Markers',
      icon: MapPin,
      fields: [
        { key: 'GPS Latitude', value: 'Pending Module Integration' },
        { key: 'GPS Longitude', value: 'Pending Module Integration' },
        { key: 'Altitude / Reference', value: 'Pending Module Integration' },
        { key: 'DateTimeOriginal', value: 'Pending Module Integration' },
        { key: 'SubSecTime', value: 'Pending Module Integration' },
      ]
    },
    {
      title: 'Encoding & Container Headers',
      icon: Layers,
      fields: [
        { key: 'Software / Editing Tool', value: 'Pending Module Integration' },
        { key: 'Color Space / ICC Profile', value: 'Pending Module Integration' },
        { key: 'Compression Scheme', value: 'Pending Module Integration' },
        { key: 'JFIF Version / Markers', value: 'Pending Module Integration' },
        { key: 'Metadata Strip Analysis', value: 'Pending Module Integration' },
      ]
    }
  ];

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
      <div style={{ marginBottom: '28px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <FileSearch size={18} color="var(--cyber-purple)" />
          <span className="mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            METADATA & EXIF FORENSIC SUITE // VIDHI HOOK
          </span>
        </div>
        <h2 style={{ fontSize: '28px', fontWeight: 800, margin: 0 }}>
          Digital Metadata & Header Analysis
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginTop: '4px' }}>
          Examine camera hardware signatures, ICC profiles, quantization tables, and tamper timestamps.
        </p>
      </div>

      <div style={{
        backgroundColor: 'rgba(139, 92, 246, 0.08)',
        border: '1px solid rgba(139, 92, 246, 0.3)',
        borderRadius: '10px',
        padding: '16px 20px',
        marginBottom: '28px',
        display: 'flex',
        alignItems: 'center',
        gap: '14px'
      }}>
        <Clock size={20} color="var(--cyber-purple)" style={{ flexShrink: 0 }} />
        <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
          <strong style={{ color: 'var(--text-primary)' }}>Architecture Status:</strong> The metadata extraction backend module is currently in active staging by Vidhi. The UI is pre-wired to bind to the schema once the FastAPI router is deployed.
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
        {metadataBlocks.map((block) => {
          const Icon = block.icon;
          return (
            <div key={block.title} className="cyber-card">
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                borderBottom: '1px solid var(--border-subtle)',
                paddingBottom: '12px',
                marginBottom: '16px'
              }}>
                <Icon size={18} color="var(--cyber-purple)" />
                <h4 style={{ fontSize: '14px', fontWeight: 700, margin: 0 }}>{block.title}</h4>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {block.fields.map((f) => (
                  <div key={f.key} style={{
                    display: 'flex',
                    flexDirection: 'column',
                    padding: '8px 10px',
                    backgroundColor: 'rgba(5, 8, 17, 0.5)',
                    borderRadius: '6px',
                    border: '1px solid var(--border-subtle)'
                  }}>
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{f.key}</span>
                    <span className="mono" style={{ fontSize: '12px', color: 'var(--text-secondary)', fontStyle: 'italic' }}>
                      {f.value}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
