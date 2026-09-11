import React, { useState, useEffect } from 'react';
import { Sparkles, AlertCircle, RefreshCw } from 'lucide-react';
import WorkflowStepper from '../common/WorkflowStepper';
import UploadZone from './UploadZone';
import ScanningOverlay from './ScanningOverlay';
import ResultCard from './ResultCard';
import GradCAMViewer from './GradCAMViewer';
import ImageDetailsCard from './ImageDetailsCard';
import MetadataSummaryCard from './MetadataSummaryCard';
import ForensicChecksGrid from './ForensicChecksGrid';
import TrustScoreGauge from './TrustScoreGauge';
import ActionButtons from './ActionButtons';
import { analyzeImage } from '../../services/api';

export default function ImageAnalysisView({ 
  onViewReport, 
  backendOnline, 
  onRecordHistory,
  persistedEvidence,
  persistedResult
}) {
  const [selectedFile, setSelectedFile] = useState(persistedEvidence || null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [dimensions, setDimensions] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(persistedResult || null);
  const [errorMessage, setErrorMessage] = useState(null);
  const [currentStep, setCurrentStep] = useState(persistedResult ? 'report' : 'upload');

  // Handle file preview and calculate dimensions
  useEffect(() => {
    if (selectedFile) {
      const url = URL.createObjectURL(selectedFile);
      setPreviewUrl(url);

      const img = new Image();
      img.onload = () => {
        setDimensions({ width: img.naturalWidth, height: img.naturalHeight });
      };
      img.src = url;

      return () => URL.revokeObjectURL(url);
    } else {
      setPreviewUrl(null);
      setDimensions(null);
    }
  }, [selectedFile]);

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setAnalysisResult(null);
    setErrorMessage(null);
    setCurrentStep('upload');
  };

  const handleClearFile = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setAnalysisResult(null);
    setErrorMessage(null);
    setCurrentStep('upload');
  };

  const handleStartAnalysis = async () => {
    if (!selectedFile) return;

    setIsScanning(true);
    setErrorMessage(null);
    setAnalysisResult(null);
    setCurrentStep('scanning');

    try {
      // Direct call to FastAPI backend: POST /api/analyze/image
      const data = await analyzeImage(selectedFile);
      setAnalysisResult(data);


      // Record to history vault
      if (onRecordHistory) {
        onRecordHistory({
          id: `SCAN-${Math.floor(1000 + Math.random() * 9000)}`,
          filename: selectedFile.name,
          analysisType: 'Image Forensics',
          verdict: data.predicted_class,
          confidence: parseFloat((data.confidence * 100).toFixed(2)),
          timestamp: new Date().toISOString().replace('T', ' ').slice(0, 19) + ' UTC',
          status: 'Completed',
          gradcam_path: data.gradcam_path,
          file: selectedFile,
          result: data,
        });
      }
    } catch (err) {
      console.error('Analysis failed:', err);
      setErrorMessage(err.message || 'Analysis failed. Check if backend is running on http://127.0.0.1:8000.');
      setCurrentStep('upload');
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
      {/* Visual Hero Message */}
      <div style={{
        marginBottom: '28px',
        display: 'flex',
        flexDirection: 'column',
        gap: '6px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="badge badge-cyan" style={{ fontSize: '10px' }}>
            DEEP CONVOLUTIONAL INFERENCE
          </span>
          <span className="mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            EVALUATING PIXEL LATENTS & ACTIVATION MAPS
          </span>
        </div>

        <h2 style={{
          fontSize: '34px',
          fontWeight: 800,
          letterSpacing: '-0.02em',
          margin: 0
        }}>
          <span className="text-gradient-cyan">Truth in Every Pixel</span>
        </h2>

        <p style={{
          color: 'var(--text-secondary)',
          fontSize: '15px',
          maxWidth: '680px',
          lineHeight: 1.5
        }}>
          Analyze digital evidence using AI-powered forensic techniques. Examine convolutional features and verify authenticity with scientific rigor.
        </p>
      </div>

      {/* Analysis Workflow Indicator */}
      <WorkflowStepper currentStep={currentStep} />

      {/* Backend Offline Warning Banner */}
      {!backendOnline && (
        <div style={{
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid var(--status-ai-border)',
          borderRadius: '8px',
          padding: '14px 18px',
          marginBottom: '24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '12px',
          color: 'var(--status-ai)',
          fontSize: '13px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <AlertCircle size={18} />
            <span>
              <strong>Backend Disconnected:</strong> FastAPI server is not responding at <code>http://127.0.0.1:8000</code>. Run <code>python -m uvicorn api.main:app --host 127.0.0.1 --port 8000</code> in <code>ai_detection</code>.
            </span>
          </div>
        </div>
      )}

      {/* Error Message Box */}
      {errorMessage && (
        <div style={{
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid var(--status-ai-border)',
          borderRadius: '8px',
          padding: '14px 18px',
          marginBottom: '24px',
          color: 'var(--status-ai)',
          fontSize: '13px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px'
        }}>
          <AlertCircle size={18} />
          <div>
            <strong>Inference Request Error:</strong> {errorMessage}
          </div>
        </div>
      )}

      {/* Step 1: Upload Zone */}
      <UploadZone
        onFileSelect={handleFileSelect}
        selectedFile={selectedFile}
        previewUrl={previewUrl}
        onClearFile={handleClearFile}
        onStartAnalysis={handleStartAnalysis}
        isScanning={isScanning}
        backendOnline={backendOnline}
      />

      {/* Step 2: Scanning Overlay (Displayed during inference) */}
      {isScanning && (
        <ScanningOverlay
          previewUrl={previewUrl}
          filename={selectedFile?.name || 'evidence.jpg'}
        />
      )}

      {/* Step 3: Analysis Results Section */}
      {analysisResult && !isScanning && (
        <div>
          {/* Main Verdict Card */}
          <ResultCard result={analysisResult} />

          {/* Grad-CAM Visualization Card */}
          <GradCAMViewer
            originalUrl={previewUrl}
            gradcamPath={analysisResult.gradcam_path}
            filename={selectedFile?.name}
          />

          {/* Technical Image Details Card */}
          <ImageDetailsCard
            file={selectedFile}
            dimensions={dimensions}
            analysisTimestamp={new Date().toISOString().replace('T', ' ').slice(0, 19) + ' UTC'}
          />

          {/* Auxiliary Forensic Components */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px' }}>
            {/* Metadata Summary */}
            <MetadataSummaryCard />

            {/* Classical Forensic Checks Grid */}
            <ForensicChecksGrid />

            {/* Digital Evidence Trust Score Gauge */}
            <TrustScoreGauge aiResult={analysisResult} />
          </div>

          {/* Actions Bar */}
          <ActionButtons
            onViewFullReport={() => onViewReport(selectedFile, analysisResult, previewUrl)}
            hasResult={!!analysisResult}
          />
        </div>
      )}
    </div>
  );
}
