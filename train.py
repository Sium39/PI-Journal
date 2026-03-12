from ultralytics import YOLO
from multiprocessing import freeze_support

def main():
    # Load a pretrained YOLO12n model
    model = YOLO("yolo12n.pt")

    # Train the model on the COCO8 dataset for 100 epochs
    train_results = model.train(
        data="C:\\Users\\SiumNSL\\Pi_Journal\\Container_Defect_Detection_Preprocessed\\data.yaml",  
        epochs=100,
        imgsz=640,
        device=0,
    )

    # Evaluate on the validation set
    metrics = model.val()

    # Export to ONNX format
    onnx_path = model.export(format="onnx")
    print(f"Exported ONNX model to: {onnx_path}")

if __name__ == "__main__":
    # Required on Windows if your code uses multiprocessing
    freeze_support()
    main()
