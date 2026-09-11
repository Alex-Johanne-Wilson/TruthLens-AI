# TruthLens AI — My Tasks (Deepfake Module)

## Current repo status
- Checkpoint 1 done: AI-generated vs real image classifier (EfficientNet-B0), Grad-CAM, `/api/analyze/image` endpoint, frontend upload flow.
- Deepfake pipeline is a skeleton only: `video.py`, `face_detection.py`, `model.py` (ResNet-18), `inference.py` exist but model is untrained.
- `/api/analyze/deepfake` currently always returns `status: "prototype"` — result is discarded, never real.
- No feature branches yet — everything is on `main`. Work on branch `alex-deepfake`.
- Don't touch Alec's (forensics) or Vidhi's (metadata/integration) files.

## Phase 2 — Deepfake (my task)

### 1. Get a dataset
- [ ] Choose FaceForensics++ or DFDC (whichever the team can access)
- [ ] Download and set up dataset directory
- [ ] Write a loader (similar to `ai_detection/src/dataset.py`, adapted for video frames)

### 2. Train the model
- [ ] Extend/write training script (mirror `ai_detection/src/train.py`)
- [ ] Use existing pipeline: `video.py` (frame sampling) → `face_detection.py` → face crop → `model.py` (ResNet-18)
- [ ] Save checkpoint to `ai_detection/outputs/checkpoints/` — use a new filename, do NOT overwrite `best_model.pth` (belongs to image detector)

### 3. Evaluate
- [ ] Compute accuracy, precision, recall, F1, confusion matrix (mirror `ai_detection/src/evaluate.py`)
- [ ] Save results to `ai_detection/outputs/evaluation/`

### 4. Wire to API
- [ ] Fix `ai_detection/api/routes/deepfake.py`
- [ ] Replace prototype-only response with real fake/real prediction + probability from trained model

## While teammates work
- [ ] Don't modify Alec's or Vidhi's files
- [ ] Don't push directly to `main`
- [ ] Work on branch `alex-deepfake`
- [ ] Review PRs from `alec-forensics` and `vidhi-integration` when ready

## Phase 3+ — After all three modules exist
- [ ] Agree on common output schema (prediction + probabilities per module) before merging
- [ ] Feed deepfake output into shared Trust Score aggregator (Vidhi builds aggregator)
- [ ] Expand frontend video flow: Upload → Frame Analysis → Face Detection → Deepfake Detection → Suspicious Frames → Result
- [ ] Run full test matrix:
  - Real video ✅
  - Deepfake video ✅
  - Corrupt file ❌
  - Unsupported format ❌
  - Very large file ❌
  - Empty upload ❌
- [ ] Tag Checkpoint 2 once verified
- [ ] Prep explanation of AI/deepfake portion for viva
- [ ] Contribute to report/PPT (AI model, forensic techniques, trust score methodology sections)

## Immediate next action
Pick dataset (FaceForensics++ vs DFDC) → start training script.
