"""训练辅助工具函数"""
import os
import sys
import csv
import pandas as pd
from pathlib import Path


def export_detailed_results(results_path: str, output_csv: str):
    """
    将 Ultralytics 生成的 results.csv 转换为更详细的格式

    参数:
        results_path: Ultralytics 生成的 results.csv 路径
        output_csv: 输出 CSV 文件路径
    """
    if not os.path.exists(results_path):
        print(f"Warning: {results_path} not found")
        return None

    df = pd.read_csv(results_path)

    # 重命名列以更清晰
    column_mapping = {
        'epoch': 'epoch',
        'train/box_loss': 'box_loss',
        'train/cls_loss': 'class_loss',
        'train/dfl_loss': 'dfl_loss',
        'metrics/precision(B)': 'precision',
        'metrics/recall(B)': 'recall',
        'metrics/mAP50(B)': 'mAP50',
        'metrics/mAP50-95(B)': 'mAP50_95',
        'val/box_loss': 'val_box_loss',
        'val/cls_loss': 'val_class_loss',
        'val/dfl_loss': 'val_dfl_loss',
        'lr/pg0': 'learning_rate',
    }

    # 仅重命名存在的列
    df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns}, inplace=True)

    df.to_csv(output_csv, index=False)
    return output_csv


def check_gpu():
    """检查 GPU 可用性"""
    import torch
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        memory = torch.cuda.get_device_properties(0).total_memory / 1024 ** 3
        print(f"✅ GPU 可用: {gpu_name}, 显存: {memory:.1f} GB")
        return True, gpu_name, memory
    else:
        print("❌ GPU 不可用，将使用 CPU 训练")
        return False, "CPU", 0


def get_optimal_batch_size(gpu_memory_gb: float, model_size: str = "n"):
    """根据 GPU 显存估算合适的 batch size"""
    # 基于 RTX 4060 Laptop 8GB 的推荐值
    # 参考：8GB 显存时 batch 建议 16 左右
    if gpu_memory_gb >= 16:
        return 32 if model_size in ["n", "s"] else 24
    elif gpu_memory_gb >= 8:
        return 16 if model_size in ["n", "s"] else 12
    elif gpu_memory_gb >= 4:
        return 8 if model_size in ["n", "s"] else 4
    else:
        return 4


def print_training_summary(results):
    """打印训练结果摘要"""
    if results is None:
        print("No training results available")
        return

    print("\n" + "=" * 60)
    print("训练完成！")
    print("=" * 60)

    # 尝试获取最佳模型指标
    try:
        metrics = results.results_dict if hasattr(results, 'results_dict') else {}
        if metrics:
            print(f"最佳 mAP50: {metrics.get('metrics/mAP50(B)', 'N/A'):.4f}")
            print(f"最佳 mAP50-95: {metrics.get('metrics/mAP50-95(B)', 'N/A'):.4f}")
    except:
        print("无法解析详细指标，请查看训练日志")

    # 显示模型保存路径
    if hasattr(results, 'save_dir'):
        print(f"\n模型保存路径: {results.save_dir}")