"""
Script to prepare a 5,000-image subset from Parveshiiii/AI-vs-Real
without loading the entire dataset into memory or modifying images.
"""

import io
import json
import os
import random
from pathlib import Path
from PIL import Image
import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download

# Configuration constants
SEED = 42
TOTAL_PER_CLASS = 2500
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

TRAIN_COUNT = int(TOTAL_PER_CLASS * TRAIN_RATIO)  # 1750
VAL_COUNT = int(TOTAL_PER_CLASS * VAL_RATIO)      # 375
TEST_COUNT = TOTAL_PER_CLASS - TRAIN_COUNT - VAL_COUNT  # 375

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

LABEL_MAPPING = {
    0: "ai_generated",
    1: "real"
}

def create_directories():
    """Ensure directory structure exists."""
    for split in ["train", "val", "test"]:
        for category in ["real", "ai_generated"]:
            (DATA_DIR / split / category).mkdir(parents=True, exist_ok=True)

def extract_and_save_images(parquet_path, selected_indices, class_label, class_name):
    """
    Reads rows from parquet file in batches and writes raw bytes to disk
    without resizing, augmenting, or altering the images.
    """
    pf = pq.ParquetFile(parquet_path)
    
    # Map index to target split:
    # 0 -> TRAIN_COUNT: train
    # TRAIN_COUNT -> TRAIN_COUNT + VAL_COUNT: val
    # TRAIN_COUNT + VAL_COUNT -> end: test
    index_to_split = {}
    for rank, idx in enumerate(selected_indices):
        if rank < TRAIN_COUNT:
            split = "train"
        elif rank < TRAIN_COUNT + VAL_COUNT:
            split = "val"
        else:
            split = "test"
        index_to_split[idx] = (split, rank)

    selected_set = set(selected_indices)
    
    saved_counts = {"train": 0, "val": 0, "test": 0}
    current_row_offset = 0

    print(f"Extracting {len(selected_indices)} images for class '{class_name}' from {parquet_path.name}...")
    
    for rg_idx in range(pf.num_row_groups):
        table = pf.read_row_group(rg_idx, columns=["image", "binary_label"])
        num_rows = table.num_rows
        
        images_col = table["image"]
        labels_col = table["binary_label"].to_pylist()
        
        for local_idx in range(num_rows):
            global_idx = current_row_offset + local_idx
            if global_idx in selected_set:
                target_split, rank = index_to_split[global_idx]
                expected_label = labels_col[local_idx]
                assert expected_label == class_label, f"Label mismatch: expected {class_label}, got {expected_label}"
                
                img_struct = images_col[local_idx].as_py()
                img_bytes = img_struct.get("bytes")
                
                # Determine extension without re-encoding
                # Check header magic bytes
                if img_bytes.startswith(b"\x89PNG"):
                    ext = ".png"
                elif img_bytes.startswith(b"\xff\xd8"):
                    ext = ".jpg"
                elif img_bytes.startswith(b"RIFF") and b"WEBP" in img_bytes[:16]:
                    ext = ".webp"
                else:
                    ext = ".jpg"
                
                filename = f"{class_name}_{rank:04d}{ext}"
                out_path = DATA_DIR / target_split / class_name / filename
                
                with open(out_path, "wb") as f:
                    f.write(img_bytes)
                
                saved_counts[target_split] += 1
                
        current_row_offset += num_rows

    print(f"Finished '{class_name}': {saved_counts}")
    return saved_counts

def main():
    random.seed(SEED)
    create_directories()
    
    # Download/resolve shard 0 (real images) and shard 1 (AI images)
    print("Downloading/locating Parquet shards...")
    shard0 = Path(hf_hub_download(
        repo_id="Parveshiiii/AI-vs-Real",
        repo_type="dataset",
        filename="data/train-00000-of-00005.parquet"
    ))
    shard1 = Path(hf_hub_download(
        repo_id="Parveshiiii/AI-vs-Real",
        repo_type="dataset",
        filename="data/train-00001-of-00005.parquet"
    ))
    
    # Shard 0 has 4000 real images (label 1) -> sample 2500 using SEED
    all_real_indices = list(range(4000))
    selected_real_indices = random.sample(all_real_indices, TOTAL_PER_CLASS)
    
    # Shard 1 has 2500 AI images (label 0) -> shuffle indices using SEED
    all_ai_indices = list(range(2500))
    selected_ai_indices = list(all_ai_indices)
    random.shuffle(selected_ai_indices)
    
    real_counts = extract_and_save_images(shard0, selected_real_indices, class_label=1, class_name="real")
    ai_counts = extract_and_save_images(shard1, selected_ai_indices, class_label=0, class_name="ai_generated")
    
    # Clean up empty placeholder gitkeeps inside old locations if needed
    for old_gitkeep in [DATA_DIR / "real" / ".gitkeep", DATA_DIR / "ai_generated" / ".gitkeep"]:
        if old_gitkeep.exists():
            old_gitkeep.unlink()
    if (DATA_DIR / "real").exists():
        try:
            (DATA_DIR / "real").rmdir()
        except OSError:
            pass
    if (DATA_DIR / "ai_generated").exists():
        try:
            (DATA_DIR / "ai_generated").rmdir()
        except OSError:
            pass

    # Create dataset_info.json metadata file
    dataset_info = {
        "dataset_name": "AI-vs-Real",
        "source": "https://huggingface.co/datasets/Parveshiiii/AI-vs-Real",
        "author": "Parveshiiii",
        "random_seed": SEED,
        "label_mapping": LABEL_MAPPING,
        "total_images": TOTAL_PER_CLASS * 2,
        "class_counts": {
            "real": TOTAL_PER_CLASS,
            "ai_generated": TOTAL_PER_CLASS
        },
        "splits": {
            "train": {
                "real": real_counts["train"],
                "ai_generated": ai_counts["train"],
                "total": real_counts["train"] + ai_counts["train"]
            },
            "val": {
                "real": real_counts["val"],
                "ai_generated": ai_counts["val"],
                "total": real_counts["val"] + ai_counts["val"]
            },
            "test": {
                "real": real_counts["test"],
                "ai_generated": ai_counts["test"],
                "total": real_counts["test"] + ai_counts["test"]
            }
        },
        "preprocessing_applied": "None. Raw unmodified bytes extracted directly from source Parquet."
    }
    
    info_path = DATA_DIR / "dataset_info.json"
    with open(info_path, "w", encoding="utf-8") as f:
        json.dump(dataset_info, f, indent=2)
    print(f"Saved dataset info to {info_path}")

if __name__ == "__main__":
    main()
