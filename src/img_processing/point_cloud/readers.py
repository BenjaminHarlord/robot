"""
专业级 S3DIS 数据集读取器
- 自动处理 .txt (点云) + .labels (标签) 配对
- 内置 S3DIS 13 类标准颜色映射
- 支持内存优化分块读取
"""
import os
import numpy as np
from typing import Dict, Tuple, Optional
from .constant import S3DIS_LABEL_COLORS, S3DIS_CLASS_NAMES


def read_s3dis_room(
        pointcloud_path: str,
        label_path: Optional[str] = None,
        intensity_channel: bool = False,
        max_points: int = None
) -> Dict[str, np.ndarray]:
    """
    读取 S3DIS 房间级点云数据

    Args:
        pointcloud_path: .txt 文件路径 (格式: X Y Z R G B [I])
        label_path: .labels 文件路径 (可选, 自动匹配)
        intensity_channel: 是否包含强度通道
        max_points: 采样点数 (None=全部)

    Returns:
        {
            'points': (N,3) 3D坐标,
            'colors': (N,3) RGB颜色 (归一化到[0,1]),
            'intensity': (N,) 激光强度 (可选),
            'labels': (N,) 语义标签,
            'class_names': [str] 13类名称
        }
    """
    # 1. 自动匹配标签文件
    if label_path is None:
        base_name = os.path.splitext(os.path.basename(pointcloud_path))[0]
        label_dir = r'E:\devRoot\robot-1\datasets\viewer\S3DIS\sem8_labels_training'
        label_path = os.path.join(label_dir, "sem8_labels_training", f"{base_name}.labels")

    # 2. 读取点云数据 (.txt)
    points_data = np.loadtxt(pointcloud_path)
    points = points_data[:, :3]  # XYZ

    # 处理颜色 (归一化到 [0,1])
    colors = points_data[:, 3:6]
    if colors.max() > 1.0:  # 如果是 [0,255] 范围
        colors = colors / 255.0

    # 3. 读取标签 (.labels)
    labels = np.fromfile(label_path, dtype=np.int32)
    if max_points:
        # 内存优化：随机采样
        indices = np.random.choice(len(points), max_points, replace=False)
        points = points[indices]
        colors = colors[indices]
        labels = labels[indices]

    # 4. 标准化输出
    result = {
        'points': points,
        'colors': colors,
        'labels': labels,
        'class_names': S3DIS_CLASS_NAMES
    }

    # 5. 添加强度通道 (如果存在)
    if intensity_channel and points_data.shape[1] > 6:
        result['intensity'] = points_data[:, 6]

    # 6. 校验维度一致性
    assert len(points) == len(labels), f"维度不匹配: {len(points)} vs {len(labels)}"
    return result