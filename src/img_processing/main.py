import open3d as o3d
import numpy as np
from point_cloud import load_pointcloud, S3DIS_LABEL_COLORS

# 1. 加载数据
data = load_pointcloud(
    data_path=r"E:\devRoot\robot-1\datasets\viewer\S3DIS\bildstein_station1_xyz_intensity_rgb\bildstein_station1_xyz_intensity_rgb.txt"
)

# 2. 创建点云
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(data['points'])
pcd.colors = o3d.utility.Vector3dVector(S3DIS_LABEL_COLORS[data['labels']])

# 3. 关键修复：用 Visualizer 代替 draw_geometries
vis = o3d.visualization.Visualizer()
vis.create_window(window_name="S3DIS 语义分割", width=1280, height=720)
vis.add_geometry(pcd)

# 4. 设置渲染参数（防止黑屏/闪退）
vis.get_render_option().point_size = 2.0
vis.get_render_option().background_color = np.array([0.0, 0.0, 0.0])  # 黑色背景

# 5. 重要！保持窗口打开直到手动关闭
print("\n💡 操作指南:")
print("  - 按住左键拖动: 旋转视角")
print("  - 按住中键拖动: 平移视角")
print("  - 滚轮: 缩放")
print("  - 按 Q: 退出窗口")
vis.run()  # 阻塞调用，确保窗口不关闭

vis.destroy_window()