"""
点云数据集通用加载器
支持: S3DIS, KITTI, nuScenes 等
"""
from .readers import read_s3dis_room
from .constant import S3DIS_CLASS_NAMES, S3DIS_LABEL_COLORS

def load_pointcloud(
    data_path: str,
    label_path: str = None,
    dataset_type: str = "auto"
) -> dict:
    """智能加载点云数据 (推荐使用)"""
    if dataset_type == "s3dis" or "s3dis" in data_path.lower():
        return read_s3dis_room(data_path, label_path)
    # ... 其他数据集支持 (后续扩展)
    raise ValueError(f"Unsupported dataset: {dataset_type}")

__all__ = [
    'load_pointcloud',
    'read_s3dis_room',
    'S3DIS_CLASS_NAMES',
    'S3DIS_LABEL_COLORS'
]