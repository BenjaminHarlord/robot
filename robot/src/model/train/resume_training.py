"""
YOLOv26 训练恢复脚本
用法: python resume_training.py
"""

from ultralytics import YOLO
import os

# ========== 配置区域 ==========
# 1. 要恢复的 checkpoint 路径（通常是 last.pt 或 best.pt）
checkpoint_path = r"～PATH_CHECKPOINT"
total_epochs = 3
def resume_training():

# 2. 继续训练的总轮数（例如原来训练了50轮，想总共训练200轮，这里填200）
#    注意：模型会自动从checkpoint中记录的epoch继续，你需要设置的是最终的总epochs
    total_epochs = 200


# 3. 其他训练参数（可选，默认使用checkpoint中保存的参数）
#    如果想修改batch/imgsz等，可以在这里指定
# resume_args = {
#     'batch': 16,
#     'imgsz': 640,
#     'device': 0,
#     'workers': 8,
# }
# ===========================

def resume_training():
    # 检查checkpoint是否存在
    if not os.path.exists(checkpoint_path):
        print(f"❌ Checkpoint not found: {checkpoint_path}")
        return

    print(f"✅ Loading checkpoint: {checkpoint_path}")
    model = YOLO(checkpoint_path)

    # 恢复训练
    # 关键参数：resume=True 会自动从checkpoint中的epoch继续
    #           如果想增加总epochs，需要额外设置epochs参数（表示最终的总epoch数）
    #           例如模型已经训练了50轮，设置epochs=200，则会继续训练150轮
    print(f"🚀 Resuming training to {total_epochs} total epochs...")

    # 方式1：使用 resume=True（推荐）
    results = model.train(resume=True, epochs=total_epochs)

    # 方式2：如果不使用resume=True，直接指定模型和参数（需要手动继承数据）
    # results = model.train(data='./yolo_src/datasets/coco/yolosets/data.yaml',
    #                       epochs=total_epochs,
    #                       resume=True)

    print("✅ Training resumed and completed!")
    print(f"📁 Results saved in: {model.trainer.save_dir}")


if __name__ == "__main__":
    resume_training()