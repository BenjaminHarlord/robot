"""YOLOv26 训练核心模块"""
import os
import csv
import torch
from pathlib import Path
from ultralytics import YOLO
from datetime import datetime


class YOLOTrainer:
    """YOLOv26 训练器类，封装训练、验证、结果导出功能"""

    def __init__(self,
                 model_name: str = "yolo26n.pt",
                 data_yaml: str = "./yolo_src/datasets/coco/yolosets/data.yaml",
                 epochs: int = 100,
                 batch: int = 16,
                 imgsz: int = 640,
                 device: int = 0,
                 workers: int = 8,
                 project: str = "./yolo_src/model/",
                 name: str = None):
        """
        初始化 YOLO 训练器

        参数:
            model_name: 模型名称（如 'yolo26n.pt', 'yolo26s.yaml'）
            data_yaml: 数据集配置文件路径
            epochs: 训练轮数
            batch: 批次大小（根据 GPU 显存调整）
            imgsz: 输入图像尺寸
            device: GPU 设备编号（0 表示第一个 GPU）
            workers: 数据加载线程数
            project: 训练结果保存根目录
            name: 实验名称（默认自动生成时间戳）
        """
        self.model_name = model_name
        self.data_yaml = data_yaml
        self.epochs = epochs
        self.batch = batch
        self.imgsz = imgsz
        self.device = device
        self.workers = workers
        self.project = project
        self.name = name or f"yolo26_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 加载模型
        self.model = YOLO(model_name)
        self.results = None

    def train(self, callback=None):
        """
        执行训练

        参数:
            callback: 可选的回调函数，接收 (epoch, metrics) 用于实时更新 UI
        """
        # 确保数据配置文件存在
        if not os.path.exists(self.data_yaml):
            raise FileNotFoundError(f"Dataset config not found: {self.data_yaml}")

        # 训练参数配置
        train_args = {
            'data': self.data_yaml,
            'epochs': self.epochs,
            'batch': self.batch,
            'imgsz': self.imgsz,
            'device': self.device,
            'workers': self.workers,
            'project': self.project,
            'name': self.name,
            'exist_ok': True,
            'pretrained': True,
            'optimizer': 'SGD',
            'lr0': 0.001,
            'lrf': 0.01,
            'warmup_epochs': 5,
            'warmup_momentum': 0.8,
            'warmup_bias_lr': 0.1,
            'mosaic': 0.5,
            'mixup': 0.0,
            'copy_paste': 0.0,
            'auto_augment': None,  # 关闭自动增强
            'degrees': 0.0,
            'translate': 0.1,
            'scale': 0.5,
            'shear': 0.0,
            'perspective': 0.0,
            'flipud': 0.0,
            'fliplr': 0.5,
            'hsv_h': 0.015,
            'hsv_s': 0.7,
            'hsv_v': 0.4,

            'seed': 42,
            'patience': 30,  # 可以适当降低
            'save': True,
            'save_period': 10,
            'val': True,
            'plots': True,
        }

        # 执行训练
        self.results = self.model.train(**train_args)
        return self.results

    def validate(self):
        """在验证集上评估模型"""
        if self.results is None:
            raise RuntimeError("Model not trained yet. Call train() first.")
        val_results = self.model.val()
        return val_results

    def export_csv(self, output_path: str = None):
        """
        将训练结果导出为 CSV

        参数:
            output_path: CSV 输出路径（默认保存到模型目录下的 training_results.csv）
        """
        if self.results is None:
            raise RuntimeError("Model not trained yet. Call train() first.")

        if output_path is None:
            output_path = os.path.join(self.project, self.name, 'training_results.csv')

        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 提取训练指标
        # 从 results.results 中提取每个 epoch 的指标
        # Ultralytics 默认保存 results.csv 到训练目录，我们直接读取并复制一份
        source_csv = os.path.join(self.project, self.name, 'results.csv')
        if os.path.exists(source_csv):
            import shutil
            shutil.copy(source_csv, output_path)
            print(f"Training results saved to {output_path}")
        else:
            print(f"Warning: results.csv not found at {source_csv}")

        return output_path

    def get_training_metrics(self):
        """获取训练过程中的指标（用于 TUI/Qt 实时显示）"""
        results_path = os.path.join(self.project, self.name, 'results.csv')
        if not os.path.exists(results_path):
            return None

        import pandas as pd
        df = pd.read_csv(results_path)
        # 返回最新一行的指标
        if len(df) > 0:
            latest = df.iloc[-1].to_dict()
            return latest
        return None