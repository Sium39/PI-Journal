# YOLOv12n Container Defect Detection

A lightweight YOLOv12n-based defect detection project for identifying **dent**, **hole**, and **rust** on container surfaces, designed for fast validation, reproducible testing, and edge-ready deployment. This project uses a public Roboflow dataset with 13,583 images and reports strong test performance on a 1,358-image test split.

---

## YOLOv12n Container Defect Detection - Key Features

- YOLOv12n-based defect detection for dent, hole, and rust
- Fast testing workflow for full validation and single-image inference
- Supports paper-ready result generation including metrics CSV and prediction images
- Uses 640x640 preprocessing with fit resize and black padding
- Includes augmentation-aware dataset preparation pipeline
- Edge-friendly lightweight model with 2.6M parameters
- Export-ready for ONNX and TensorFlow Lite deployment

---

## YOLOv12n Container Defect Detection - Project Overview

This repository focuses on container defect detection using YOLOv12n. The project is designed so that anyone can install the dependencies, load the trained `best.pt` model, run the test script, and verify the reported results on the test set.

Target classes:

- dent
- hole
- rust

---

## YOLOv12n Container Defect Detection - Reported Performance

| Metric | Score |
|--------|-------|
| Accuracy | 92.93 |
| Precision | 91.77 |
| Recall | 91.85 |
| F1-Score | 92.27 |
| mAP50 | 82.45 |
| mAP50-95 | 52.19 |
| Inference Speed | 3.5 ms |
| Parameters | 2.6M |

### Per-Class Results

| Class | Accuracy | Precision | Recall | F1-Score |
|------|----------|-----------|--------|----------|
| dent | 92.8 | 91.4 | 90.9 | 91.1 |
| hole | 93.2 | 91.6 | 92.7 | 92.9 |
| rust | 92.9 | 92.2 | 91.8 | 92.5 |
| Average | 92.9 | 91.7 | 91.8 | 92.2 |

---

## YOLOv12n Container Defect Detection - Dataset

The project uses a public container defect detection dataset from Roboflow.

| Split | Images |
|------|--------|
| Train | 10,867 |
| Validation | 1,358 |
| Test | 1,358 |
| Total | 13,583 |

### Classes

- dent
- hole
- rust

---

## YOLOv12n Container Defect Detection - Preprocessing and Augmentation

### Preprocessing
- Auto-Orient applied
- Resize: Fit with black edges
- Output image size: 640x640

### Augmentations
- Outputs per training example: 3
- Rotate: 90 degrees clockwise and counter-clockwise
- Hue: between -15 and 15
- Saturation: between -25 and 25
- Exposure: between -15 and 15
- Noise: up to 6% of pixels

---

## YOLOv12n Container Defect Detection - Project Structure

```bash
YOLOv12n-Container-Defect-Detection/
├── README.md
├── requirements.txt
├── dataset.yaml
├── preprocess.py
├── testmodel.py
├── singletestsave.py
├── runs/
│   └── detect/
│       └── train/
│           └── weights/
│               └── best.pt
├── testresults/
│   ├── yolov12n_test_metrics.csv
│   ├── yolov12n_test_predictions.png
│   └── *.json
└── sample_images/
    └── test.jpg
YOLOv12n Container Defect Detection - Requirements
Install the required Python packages:

bash
pip install ultralytics==8.3.0 opencv-python matplotlib pandas numpy albumentations scikit-learn seaborn
You can also place them in requirements.txt:

text
ultralytics==8.3.0
opencv-python
matplotlib
pandas
numpy
albumentations
scikit-learn
seaborn
YOLOv12n Container Defect Detection - Quick Start
1. Clone the project
bash
git clone <your-repo-url>
cd YOLOv12n-Container-Defect-Detection
2. Install dependencies
bash
pip install -r requirements.txt
3. Make sure the trained model exists
Expected model path:

bash
runs/detect/train/weights/best.pt
4. Check dataset configuration
Expected dataset file:

bash
dataset.yaml
Example:

text
path: ./ContainerDefectDetectionPreprocessed
train: train/images
val: val/images
test: test/images

nc: 4
names: ['dent', 'hole', 'rust']
YOLOv12n Container Defect Detection - Run Full Test
Run the full validation script to verify the reported test results:

bash
python testmodel.py --model runs/detect/train/weights/best.pt --data dataset.yaml
This script should:

load the trained YOLOv12n model

evaluate on the test split

generate validation plots

save a metrics CSV file

save sample prediction images

generate confusion matrix outputs if available

Expected Outputs
yolov12n_test_metrics.csv

yolov12n_test_predictions.png

validation plots under runs/detect/valtest/ or your configured output folder

confusion matrix image

PR curve

F1 curve

JSON predictions if enabled

YOLOv12n Container Defect Detection - Single Image Test
Run inference on a single image and save the result:

bash
python singletestsave.py --image sample_images/test.jpg
This script should:

load best.pt

run prediction on the input image

save an annotated JPG result

save a JSON file containing bounding boxes, class labels, and confidence scores

Expected Saved Files
testresults/yolov12n_test_<timestamp>.jpg

testresults/yolov12n_test_<timestamp>.json

YOLOv12n Container Defect Detection - Example VS Code Workflow
Terminal 1: Install dependencies
bash
pip install -r requirements.txt
Terminal 2: Run full validation
bash
python testmodel.py --model runs/detect/train/weights/best.pt --data dataset.yaml
Terminal 3: Run single image test
bash
python singletestsave.py --image sample_images/test.jpg
YOLOv12n Container Defect Detection - Hardware
Stage	Hardware
Training / Validation	NVIDIA RTX 5060 8GB, Ryzen 7 7800X3D
Edge Deployment	Raspberry Pi 5
Export Targets	ONNX, TFLite
YOLOv12n Container Defect Detection - Export for Edge Deployment
Export the trained model for deployment:

ONNX
bash
yolo export model=runs/detect/train/weights/best.pt format=onnx simplify=True
TensorFlow Lite
bash
yolo export model=runs/detect/train/weights/best.pt format=tflite int8=True
YOLOv12n Container Defect Detection - Example File Roles
File	Purpose
preprocess.py	Preprocesses dataset and applies augmentation
dataset.yaml	YOLO dataset configuration
testmodel.py	Runs full test-set validation
singletestsave.py	Runs single-image inference and saves outputs
best.pt	Trained YOLOv12n model weights
YOLOv12n Container Defect Detection - How to Verify Results
To verify the project:

Install dependencies.

Confirm that best.pt exists.

Confirm that dataset.yaml points to the correct dataset folders.

Run testmodel.py.

Compare the generated metrics with the reported values in this README.

Run singletestsave.py on a sample image to visually inspect predictions.

YOLOv12n Container Defect Detection - Troubleshooting
Model file not found
Make sure this file exists:

bash
runs/detect/train/weights/best.pt
Dataset path error
Open dataset.yaml and verify the paths for:

train

val

test

No predictions saved
Check whether the output folder exists:

bash
testresults/
If not, create it manually or add directory creation in the script.

Ultralytics version mismatch
Install the required version again:

bash
pip install ultralytics==8.3.0
YOLOv12n Container Defect Detection - Recommended Commands
Full test
bash
python testmodel.py --model runs/detect/train/weights/best.pt --data dataset.yaml
Single image test
bash
python singletestsave.py --image sample_images/test.jpg
Export ONNX
bash
yolo export model=runs/detect/train/weights/best.pt format=onnx simplify=True
Export TFLite
bash
yolo export model=runs/detect/train/weights/best.pt format=tflite int8=True
YOLOv12n Container Defect Detection - Status
Test-ready

Reproducible validation workflow

Paper-ready output generation

Lightweight and edge-deployable

YOLOv12n Container Defect Detection - Author
Sium Bin Noor
Graduate Researcher / Computer Vision and Deep Learning

YOLOv12n Container Defect Detection - Citation
If you use this project, please cite your corresponding paper, report, or repository documentation.

text
@article{yolov12n_container_defect_detection_2026,
  title={YOLOv12n for Container Defect Detection},
  author={Sium Bin Noor},
  journal={IEEE-style manuscript / project repository},
  year={2026}
}
text