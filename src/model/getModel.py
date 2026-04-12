import os
import torch
from ultralytics import YOLO

def save_yolo11_model():
    model = YOLO(f'yolo11n.pt')
    torch.save({
        'model_state_dict': model.model.state_dict(),
        'model_yaml': model.model.yaml,
        'names': model.names,
        'task': model.task,
        'version': 'YOLOv11'
    }, "./models/yolo11n_complete.pt")
    torch.save(model.model.state_dict(), "./models/yolo11n_weights.pt")
def save_yolo8_model():
    model = YOLO('yolov8n.pt')
    torch.save({
        'model_state_dict': model.model.state_dict(),
        'model_yaml': model.model.yaml,
        'names': model.names,
        'task': model.task,
        'version': 'YOLOv8'
    }, "./models/yolov8n_complete.pt")
    torch.save(model.model.state_dict(), "./models/yolov8n_weights.pt")
save_yolo11_model()
save_yolo8_model()