import React, { useState, useRef } from 'react';
import { 
  UserCheck, 
  Video, 
  Upload, 
  AlertTriangle, 
  ShieldAlert, 
  Film, 
  Clock, 
  RefreshCw,
  Info,
  CheckCircle2,
  X
} from 'lucide-react';
import { analyzeDeepfake } from '../../services/api';

export default function DeepfakeView() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [videoPreviewUrl, setVideoPreviewUrl] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [apiResponse, setApiResponse] = useState(null);
  const [apiError, setApiError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setVideoPreviewUrl(URL.createObjectURL(file));
      setApiResponse(null);
      setApiError(null);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    if (videoPreviewUrl) URL.revokeObjectURL(videoPreviewUrl);
    setVideoPreviewUrl(null);
    setApiResponse(null);
    setApiError(null);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    setIsAnalyzing(true);
    setApiError(null);
    try {
      const data = await analyzeDeepfake(selectedFile);
      setApiResponse(data);
    } catch (err) {
      setApiError(err.message || 'Deepfake analysis request failed');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Prototype frames timeline mockup
  const prototypeTimeline = [
    { frame: '00:01.20', risk: 'Uncalibrated', status: 'pending' },
    { frame: '00:02.40', risk: 'Uncalibrated', status: 'pending' },
    { frame: '00:03.60', risk: 'Uncalibrated', status: 'pending' },
    { frame: '00:04.80', risk: 'Uncalibrated', status: 'pending' },
  ];

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
      {/* Header Banner */}
      <div style={{ marginBottom: '28px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
          <span className="badge badge-ai" style={{ fontSize: '10px' }}>
            PROTOTYPE / MODEL VALIDATION PENDING
          </span>
          <span className="mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            ENDPOINT: POST /api/analyze/deepfake
          </span>
        </div>

        <h2 style={{ fontSize: '28px', fontWeight: 800, marginBottom: '6px' }}>
          Deepfake & Video Facial Biometric Analysis
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px', maxWidth: '750px' }}>
          Frame-by-frame temporal consistency, facial landmark jitter, and deepfake synthesis artifact examination.
        </p>
      </div>

      {/* Mandatory Prototype Notice Alert */}
      <div style={{
        backgroundColor: 'rgba(239, 68, 68, 0.08)',
        border: '1px solid var(--status-ai-border)',
        borderRadius: '10px',
        padding: '16px 20px',
        marginBottom: '28px',
        display: 'flex',
        alignItems: 'flex-start',
        gap: '14px'
      }}>
        <AlertTriangle size={22} color="var(--status-ai)" style={{ flexShrink: 0, marginTop: '2px' }} />
        <div style={{ fontSize: '13px', lineHeight: 1.5, color: 'var(--text-secondary)' }}>
          <strong style={{ color: 'var(--text-primary)' }}>Important Forensic Transparency Notice:</strong> The deepfake detection backend model is currently an <strong>untrained/unvalidated prototype</strong> undergoing benchmark verification. It is NOT calibrated for legal or court evidentiary conclusions. Inference queries directly return the backend's explicit placeholder response.
        </div>
      </div>

      {/* Upload Zone */}
      <div className="cyber-card cyber-corners" style={{ marginBottom: '28px' }}>
        {!selectedFile ? (
          <div
            onClick={() => fileInputRef.current?.click()}
            style={{
              border: '2px dashed var(--border-cyan)',
              borderRadius: '10px',
              padding: '44px 24px',
              textAlign: 'center',
              backgroundColor: 'rgba(5, 8, 17, 0.4)',
              cursor: 'pointer',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '12px'
            }}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="video/*,image/*"
              style={{ display: 'none' }}
              onChange={handleFileChange}
            />

            <div style={{
              width: '56px',
              height: '56px',
              borderRadius: '50%',
              backgroundColor: 'rgba(0, 242, 254, 0.1)',
              border: '1px solid var(--border-cyan)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Video size={26} color="var(--cyber-cyan)" />
            </div>

            <h3 style={{ fontSize: '16px', fontWeight: 700 }}>
              Select Video or Frame Sequence
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
              Upload MP4, AVI, MOV, or reference facial frame
            </p>

            <button type="button" className="btn-secondary" style={{ marginTop: '6px' }}>
              <Upload size={14} />
              Browse Media
            </button>
          </div>
        ) : (
          <div>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              borderBottom: '1px solid var(--border-subtle)',
              paddingBottom: '14px',
              marginBottom: '18px'
            }}>
              <span className="mono" style={{ fontSize: '13px', color: 'var(--cyber-cyan)', fontWeight: 600 }}>
                MEDIA: {selectedFile.name}
              </span>
              <button onClick={handleClear} className="btn-ghost" style={{ color: 'var(--status-ai)', fontSize: '12px' }}>
                <X size={14} /> Remove Media
              </button>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '20px', flexWrap: 'wrap' }}>
              {videoPreviewUrl && selectedFile.type.startsWith('video/') ? (
                <video
                  src={videoPreviewUrl}
                  controls
                  style={{ maxHeight: '200px', borderRadius: '8px', backgroundColor: '#000000' }}
                />
              ) : (
                <img
                  src={videoPreviewUrl}
                  alt="Preview"
                  style={{ maxHeight: '180px', borderRadius: '8px', backgroundColor: '#000000' }}
                />
              )}

              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '14px', fontWeight: 600 }}>Ready for Prototype Dispatch</div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Target Endpoint: <code>POST /api/analyze/deepfake</code>
                </div>
                <div style={{ marginTop: '14px' }}>
                  <button
                    onClick={handleAnalyze}
                    disabled={isAnalyzing}
                    className="btn-primary"
                  >
                    {isAnalyzing ? (
                      <>
                        <RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} />
                        Querying Backend...
                      </>
                    ) : (
                      <>
                        <UserCheck size={16} />
                        Run Prototype Deepfake Query
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* API Response Display */}
      {apiResponse && (
        <div className="cyber-card" style={{
          marginBottom: '28px',
          border: '1px solid var(--border-cyan)',
          backgroundColor: 'rgba(15, 23, 42, 0.7)'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: '1px solid var(--border-subtle)',
            paddingBottom: '12px',
            marginBottom: '14px'
          }}>
            <span className="mono" style={{ fontSize: '12px', color: 'var(--cyber-cyan)', fontWeight: 600 }}>
              ACTUAL BACKEND API RESPONSE
            </span>
            <span className="badge badge-ai" style={{ fontSize: '9px' }}>
              STATUS: {apiResponse.status}
            </span>
          </div>

          <div style={{
            padding: '16px',
            backgroundColor: 'rgba(5, 8, 17, 0.6)',
            borderRadius: '8px',
            border: '1px solid var(--border-subtle)'
          }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
              <div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>Overall Prediction</div>
                <div style={{ 
                  fontSize: '18px', 
                  fontWeight: 700, 
                  color: apiResponse.overall_prediction === 'fake' ? 'var(--status-ai)' : 'var(--cyber-cyan)' 
                }}>
                  {apiResponse.overall_prediction ? apiResponse.overall_prediction.toUpperCase() : 'UNKNOWN'}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>Confidence Score</div>
                <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)' }}>
                  {apiResponse.confidence_score ? (apiResponse.confidence_score * 100).toFixed(1) + '%' : 'N/A'}
                </div>
              </div>
            </div>

            {apiResponse.summary && (
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '16px', display: 'flex', gap: '16px', borderTop: '1px solid var(--border-subtle)', paddingTop: '12px' }}>
                <span>Analyzed Faces: {apiResponse.summary.total_analyzed_faces}</span>
                <span>Fake Frames: {apiResponse.summary.percentage_fake_predictions?.toFixed(1) || 0}%</span>
              </div>
            )}

            <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '6px' }}>
              Backend Response Message:
            </div>
            <div className="mono" style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              "{apiResponse.message}"
            </div>
          </div>
        </div>
      )}

      {/* Error state */}
      {apiError && (
        <div style={{
          padding: '14px 18px',
          borderRadius: '8px',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid var(--status-ai-border)',
          color: 'var(--status-ai)',
          fontSize: '13px',
          marginBottom: '28px'
        }}>
          <strong>API Error:</strong> {apiError}
        </div>
      )}

      {/* Frame Timeline Visualization (Design Prototype) */}
      <div className="cyber-card">
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid var(--border-subtle)',
          paddingBottom: '14px',
          marginBottom: '18px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Film size={16} color="var(--cyber-cyan)" />
            <h3 style={{ fontSize: '15px', fontWeight: 700, margin: 0 }}>
              Frame-Level Temporal Inspection Timeline (Architecture Specification)
            </h3>
          </div>
          <span className="badge badge-pending" style={{ fontSize: '9px' }}>
            FRAME HOOK SPEC
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
          {(apiResponse?.frames && apiResponse.frames.length > 0 ? apiResponse.frames : prototypeTimeline).map((item, idx) => {
            const isActualFrame = !!item.faces;
            const timeStr = isActualFrame 
              ? new Date(item.timestamp * 1000).toISOString().substr(14, 5) 
              : item.frame;
              
            const face = isActualFrame && item.faces.length > 0 ? item.faces[0] : null;
            const statusLabel = face ? (face.pred_class === 0 ? 'FAKE' : 'REAL') : (isActualFrame ? 'NO FACE' : item.status);
            const statusColor = face ? (face.pred_class === 0 ? 'var(--status-ai)' : 'var(--cyber-cyan)') : 'var(--text-muted)';
            const conf = face ? (face.pred_class === 0 ? face.fake_prob : face.real_prob) : null;
            
            return (
              <div
                key={idx}
                style={{
                  backgroundColor: 'rgba(5, 8, 17, 0.5)',
                  padding: '12px',
                  borderRadius: '8px',
                  border: '1px solid var(--border-subtle)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-muted)' }}>
                  <span className="mono">PTS: {timeStr}</span>
                  <span className="badge" style={{ fontSize: '8px', borderColor: statusColor, color: statusColor }}>
                    {statusLabel.toUpperCase()}
                  </span>
                </div>
                <div style={{
                  height: '60px',
                  margin: '8px 0',
                  backgroundColor: '#000000',
                  borderRadius: '4px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '10px',
                  color: 'var(--text-muted)',
                  fontFamily: 'var(--font-mono)'
                }}>
                  {face ? `Face Det: ${face.bbox.map(n => Math.round(n)).join(',')}` : '[Facial Keypoint ROI]'}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                  Confidence: <span className="mono" style={{ color: 'var(--text-primary)' }}>
                    {conf !== null ? (conf * 100).toFixed(1) + '%' : 'N/A'}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
