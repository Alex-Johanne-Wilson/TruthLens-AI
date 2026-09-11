import React, { useState, useRef } from 'react';
import { 
  Upload, 
  FileImage, 
  X, 
  RefreshCw, 
  Cpu, 
  CheckCircle2, 
  AlertTriangle,
  Sparkles
} from 'lucide-react';

export default function UploadZone({ 
  onFileSelect, 
  selectedFile, 
  previewUrl, 
  onClearFile, 
  onStartAnalysis,
  isScanning,
  backendOnline
}) {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      validateAndSet(file);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      validateAndSet(file);
    }
  };

  const validateAndSet = (file) => {
    const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      alert('Unsupported file format. Please upload JPG, PNG, or WEBP.');
      return;
    }
    onFileSelect(file);
  };

  // Helper to format bytes
  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Quick load standard verification sample `real_0001.jpg`
  const loadVerifiedSample = async () => {
    try {
      // Create a blob representing a forensic test pattern or fetch standard sample
      // Let's create a test image canvas to generate a valid JPEG file for immediate testing
      const canvas = document.createElement('canvas');
      canvas.width = 256;
      canvas.height = 256;
      const ctx = canvas.getContext('2d');
      // Create forensic test gradient pattern
      const grad = ctx.createLinearGradient(0, 0, 256, 256);
      grad.addColorStop(0, '#102040');
      grad.addColorStop(0.5, '#38BDF8');
      grad.addColorStop(1, '#050811');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 256, 256);
      ctx.fillStyle = '#FFFFFF';
      ctx.font = '16px monospace';
      ctx.fillText('TruthLens-Evidence', 30, 120);
      ctx.fillText('Test Sample #0001', 30, 150);

      canvas.toBlob((blob) => {
        const file = new File([blob], 'real_0001.jpg', { type: 'image/jpeg' });
        onFileSelect(file);
      }, 'image/jpeg', 0.95);
    } catch (err) {
      console.error('Failed to load sample', err);
    }
  };

  return (
    <div className="cyber-card cyber-corners" style={{ marginBottom: '28px' }}>
      {!selectedFile ? (
        /* Upload Area */
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          style={{
            border: `2px dashed ${isDragOver ? 'var(--cyber-cyan)' : 'var(--border-cyan)'}`,
            borderRadius: '10px',
            padding: '48px 24px',
            textAlign: 'center',
            backgroundColor: isDragOver ? 'rgba(0, 242, 254, 0.06)' : 'rgba(5, 8, 17, 0.4)',
            cursor: 'pointer',
            transition: 'all 0.25s ease',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '14px'
          }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".jpg,.jpeg,.png,.webp"
            style={{ display: 'none' }}
            onChange={handleFileInput}
          />

          <div style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            backgroundColor: 'rgba(0, 242, 254, 0.1)',
            border: '1px solid var(--border-cyan)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: 'var(--shadow-cyan)'
          }}>
            <Upload size={30} color="var(--cyber-cyan)" />
          </div>

          <div>
            <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '6px' }}>
              Drag & drop an image here
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
              or click to browse from your filesystem
            </p>
          </div>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '11px',
            color: 'var(--text-muted)',
            marginTop: '4px'
          }}>
            <span className="badge badge-cyan">JPG</span>
            <span className="badge badge-cyan">PNG</span>
            <span className="badge badge-cyan">WEBP</span>
            <span>• Max file size: 25MB</span>
          </div>

          <div style={{ marginTop: '12px' }}>
            <button 
              type="button" 
              className="btn-primary"
              onClick={(e) => {
                e.stopPropagation();
                fileInputRef.current?.click();
              }}
            >
              <FileImage size={16} />
              Choose File
            </button>
          </div>

          {/* Quick test sample button */}
          <div style={{
            marginTop: '16px',
            paddingTop: '16px',
            borderTop: '1px solid var(--border-subtle)',
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '12px'
          }}>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              Or quick-test verification sample:
            </span>
            <button
              type="button"
              className="btn-secondary"
              style={{ fontSize: '11px', padding: '6px 14px' }}
              onClick={(e) => {
                e.stopPropagation();
                loadVerifiedSample();
              }}
            >
              <Sparkles size={13} />
              Load Sample (real_0001.jpg)
            </button>
          </div>
        </div>
      ) : (
        /* File Selected Preview & Action Bar */
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '20px'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: '1px solid var(--border-subtle)',
            paddingBottom: '14px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span className="badge badge-cyan">EVIDENCE STAGED</span>
              <span className="mono" style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                READY FOR INFERENCE
              </span>
            </div>

            <button
              onClick={onClearFile}
              disabled={isScanning}
              className="btn-ghost"
              style={{ color: 'var(--status-ai)', fontSize: '12px', padding: '4px 10px' }}
            >
              <X size={14} />
              Remove / Replace
            </button>
          </div>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '24px',
            flexWrap: 'wrap'
          }}>
            {/* Image Preview Thumbnail */}
            <div style={{
              width: '120px',
              height: '120px',
              borderRadius: '8px',
              overflow: 'hidden',
              border: '1px solid var(--border-cyan)',
              backgroundColor: '#000000',
              position: 'relative',
              flexShrink: 0
            }}>
              <img
                src={previewUrl}
                alt="Selected evidence preview"
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover'
                }}
              />
            </div>

            {/* File Info */}
            <div style={{ flex: 1, minWidth: '220px' }}>
              <div style={{
                fontSize: '16px',
                fontWeight: 700,
                color: 'var(--text-primary)',
                wordBreak: 'break-all',
                marginBottom: '6px'
              }}>
                {selectedFile.name}
              </div>

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
                gap: '8px',
                fontSize: '12px',
                color: 'var(--text-secondary)'
              }}>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Size: </span>
                  <span className="mono" style={{ color: 'var(--text-primary)' }}>
                    {formatBytes(selectedFile.size)}
                  </span>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Format: </span>
                  <span className="mono" style={{ color: 'var(--cyber-cyan)' }}>
                    {selectedFile.type.replace('image/', '').toUpperCase()}
                  </span>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Backend: </span>
                  <span style={{
                    color: backendOnline ? 'var(--status-real)' : 'var(--status-ai)',
                    fontWeight: 600
                  }}>
                    {backendOnline ? 'Online (8000)' : 'Offline'}
                  </span>
                </div>
              </div>
            </div>

            {/* Start Analysis Button */}
            <div style={{ flexShrink: 0 }}>
              <button
                onClick={onStartAnalysis}
                disabled={isScanning}
                className="btn-primary"
                style={{
                  padding: '14px 28px',
                  fontSize: '15px'
                }}
              >
                {isScanning ? (
                  <>
                    <RefreshCw size={18} style={{ animation: 'spin 1s linear infinite' }} />
                    Forensic Scanning...
                  </>
                ) : (
                  <>
                    <Cpu size={18} />
                    Start Forensic Analysis
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
