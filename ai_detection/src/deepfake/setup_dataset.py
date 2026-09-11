import os
import json
import cv2
import numpy as np
from pathlib import Path

def setup():
    print("Generating synthetic dummy dataset due to low disk space (<150MB)...")
    
    base_dir = Path(__file__).resolve().parent.parent.parent
    data_dir = base_dir / "data" / "deepfake"
    
    label_map = {0: "fake", 1: "real"}
    
    splits = {
        "train": 100,
        "val": 20,
        "test": 20
    }
    
    stats = {}
    
    for split_name, count_per_class in splits.items():
        print(f"Generating split: {split_name} ({count_per_class} per class)")
        
        for label_name in label_map.values():
            (data_dir / split_name / label_name).mkdir(parents=True, exist_ok=True)
            
        split_stats = {"real": 0, "fake": 0}
        
        for label_int, label_name in label_map.items():
            for i in range(count_per_class):
                # Generate random color image (224, 224, 3)
                img = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
                out_path = data_dir / split_name / label_name / f"{i:05d}.jpg"
                cv2.imwrite(str(out_path), img)
                split_stats[label_name] += 1
                
        stats[split_name] = split_stats
        
    info = {
        "dataset": "synthetic_dummy",
        "label_mapping": label_map,
        "stats": stats
    }
    
    with open(data_dir / "dataset_info.json", "w") as f:
        json.dump(info, f, indent=2)
        
    print("Dataset setup complete.")

if __name__ == "__main__":
    setup()
