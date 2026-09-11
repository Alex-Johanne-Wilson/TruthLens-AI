"""
Generates the required set of Grad-CAM visualizations:
  - 3 correctly classified AI-generated images
  - 3 correctly classified Real images
  - 3 misclassified images from outputs/evaluation/misclassified.json
"""

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.gradcam import explain_image

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs" / "gradcam"
CHECKPOINT_PATH = BASE_DIR / "outputs" / "checkpoints" / "best_model.pth"
MISCLASSIFIED_PATH = BASE_DIR / "outputs" / "evaluation" / "misclassified.json"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Select 3 correctly classified AI images from test/ai_generated
correct_ai_samples = [
    DATA_DIR / "test" / "ai_generated" / "ai_generated_2125.jpg",
    DATA_DIR / "test" / "ai_generated" / "ai_generated_2126.jpg",
    DATA_DIR / "test" / "ai_generated" / "ai_generated_2127.jpg",
]

# 2. Select 3 correctly classified Real images from test/real
correct_real_samples = [
    DATA_DIR / "test" / "real" / "real_2125.jpg",
    DATA_DIR / "test" / "real" / "real_2126.jpg",
    DATA_DIR / "test" / "real" / "real_2127.jpg",
]

# 3. Select 3 misclassified images from misclassified.json
with open(MISCLASSIFIED_PATH, "r", encoding="utf-8") as f:
    misclassified_data = json.load(f)

misclassified_samples = [Path(item["file_path"]) for item in misclassified_data[:3]]

all_targets = []
# Group A: Correct AI
for idx, path in enumerate(correct_ai_samples, 1):
    out_name = "correct_ai_generated.png" if idx == 1 else f"correct_ai_generated_{idx}.png"
    all_targets.append((path, OUTPUT_DIR / out_name, f"Correct AI #{idx}"))

# Group B: Correct Real
for idx, path in enumerate(correct_real_samples, 1):
    out_name = "correct_real.png" if idx == 1 else f"correct_real_{idx}.png"
    all_targets.append((path, OUTPUT_DIR / out_name, f"Correct Real #{idx}"))

# Group C: Misclassified
for idx, path in enumerate(misclassified_samples, 1):
    out_name = "misclassified_example.png" if idx == 1 else f"misclassified_example_{idx}.png"
    all_targets.append((path, OUTPUT_DIR / out_name, f"Misclassified #{idx}"))

print(f"Generating {len(all_targets)} Grad-CAM explanations...")
results_summary = []

for img_p, out_p, label in all_targets:
    print(f"\nProcessing [{label}]: {img_p.name} -> {out_p.name}")
    report = explain_image(
        image_path=img_p,
        checkpoint_path=CHECKPOINT_PATH,
        output_path=out_p
    )
    report["category"] = label
    report["saved_as"] = str(out_p)
    results_summary.append(report)

summary_json_path = OUTPUT_DIR / "gradcam_summary.json"
with open(summary_json_path, "w", encoding="utf-8") as f:
    json.dump(results_summary, f, indent=2)

print(f"\nAll Grad-CAM visualizations generated and recorded to: {summary_json_path}")
