import os
import shutil
import random
import cv2
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
import albumentations as A
import pandas as pd

# Config
DATASET_DIR = Path("C:\\Users\\SiumNSL\\Pi_Journal\\Container_Defect_Detection")  
OUTPUT_DIR = Path("C:\\Users\\SiumNSL\\Pi_Journal\\Container_Defect_Detection_Preprocessed")
IMG_SIZE = (640, 640)
TRAIN_SPLIT = 0.8
SEED = 42
NUM_OUTPUTS = 3  # Mosaic-style augmentation

random.seed(SEED)
np.random.seed(SEED)

def verify_labels(label_path):
    """Verify YOLO label format (class x_center y_center width height)"""
    with open(label_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 5:
                return False
            cls, cx, cy, w, h = map(float, parts)
            if not (0 <= cls < 4 and 0 <= cx <= 1 and 0 <= cy <= 1 and 0 <= w <= 1 and 0 <= h <= 1):  # 4 classes
                return False
    return True

def resize_fit_black(img_path, size=(640, 640)):
    """Resize: Fit (black edges) - matches Roboflow preprocessing"""
    img = cv2.imread(str(img_path))
    h, w = img.shape[:2]
    scale = min(size[0]/w, size[1]/h)
    new_w, new_h = int(w * scale), int(h * scale)
    resized = cv2.resize(img, (new_w, new_h))
    canvas = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    top = (size[1] - new_h) // 2
    left = (size[0] - new_w) // 2
    canvas[top:top+new_h, left:left+new_w] = resized
    return canvas, left/640.0, top/640.0  # Return offsets for label adjustment if needed

# Albumentations pipeline matching your specs
transform = A.Compose([
    A.Rotate(limit=90, value=0, p=0.5),  # 90° Clockwise/Counter-Clockwise
    A.HueSaturationValue(hue_shift_limit=15, sat_shift_limit=25, val_shift_limit=15, p=0.5),
    A.RandomBrightnessContrast(brightness_limit=0.15, contrast_limit=0.15, p=0.5),
    A.GaussNoise(var_limit=(0.0, 36), p=0.3),  # ~6% pixel noise
], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))

def main():
    # Create YOLO structure
    for split in ['train', 'val']:
        (OUTPUT_DIR / split / 'images').mkdir(parents=True, exist_ok=True)
        (OUTPUT_DIR / split / 'labels').mkdir(parents=True, exist_ok=True)
    
    # Find image-label pairs
    images = list(DATASET_DIR.glob("**/*.jpg")) + list(DATASET_DIR.glob("**/*.png"))
    image_paths, label_paths = [], []
    
    for img_path in images:
        label_path = img_path.with_suffix('.txt').with_name(img_path.stem + '.txt')
        if label_path.exists() and verify_labels(label_path):
            image_paths.append(img_path)
            label_paths.append(label_path)
    
    print(f"Found {len(image_paths)} valid pairs (dent/hole/rust/background)")
    
    # 80/10/10 split
    train_imgs, temp_imgs, train_lbls, temp_lbls = train_test_split(
        image_paths, label_paths, train_size=TRAIN_SPLIT, random_state=SEED
    )
    val_imgs, test_imgs, val_lbls, test_lbls = train_test_split(
        temp_imgs, temp_lbls, test_size=0.5, random_state=SEED
    )
    
    # Process splits with augmentation
    for imgs, lbls, split in [('train', train_imgs, train_lbls), 
                             ('val', val_imgs, val_lbls), 
                             ('test', test_imgs, test_lbls)]:
        for img_path, lbl_path in zip(imgs, lbls):
            img_name = img_path.stem
            
            # Base preprocessing: Auto-Orient + Resize Fit (black edges)
            resized_img, x_offset, y_offset = resize_fit_black(img_path, IMG_SIZE)
            out_img_base = OUTPUT_DIR / split / 'images' / f"{img_name}.jpg"
            cv2.imwrite(str(out_img_base), resized_img)
            
            # Copy original labels (normalized coords preserved with padding)
            shutil.copy2(lbl_path, OUTPUT_DIR / split / 'labels' / f"{img_name}.txt")
            
            # Apply augmentations (3 versions for train only)
            if split == 'train':
                bboxes = []
                class_labels = []
                with open(lbl_path, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        cls = int(parts[0])
                        cx, cy, w, h = map(float, parts[1:])
                        bboxes.append([cx, cy, w, h])
                        class_labels.append(cls)
                
                for aug_idx in range(1, NUM_OUTPUTS + 1):
                    # Apply augmentation pipeline
                    transformed = transform(image=resized_img, bboxes=bboxes, class_labels=class_labels)
                    aug_img = transformed['image']
                    aug_bboxes = transformed['bboxes']
                    aug_labels = transformed['class_labels']
                    
                    # Save augmented version
                    aug_name = f"{img_name}_aug{aug_idx}"
                    cv2.imwrite(str(OUTPUT_DIR / split / 'images' / f"{aug_name}.jpg"), aug_img)
                    
                    # Write augmented labels
                    with open(OUTPUT_DIR / split / 'labels' / f"{aug_name}.txt", 'w') as f:
                        for bbox, cls in zip(aug_bboxes, aug_labels):
                            f.write(f"{int(cls)} {bbox[0]:.6f} {bbox[1]:.6f} {bbox[2]:.6f} {bbox[3]:.6f}\n")
    
    
    print("✅ Preprocessing + Augmentation complete!")
    print(f"📁 Output: {OUTPUT_DIR}")
    print("🚀 Ready for YOLOv12n training")

if __name__ == "__main__":
    main()
