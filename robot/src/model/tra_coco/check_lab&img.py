"""
数据集清洗脚本：只保留图片与标签文件名严格匹配的样本。
不匹配的图片和标签文件会被移动到 backups/images_orphaned 和 backups/labels_orphaned 目录下。
"""

import os
import csv
import shutil
from pathlib import Path

# ========== 用户配置 ==========
DATASET_ROOT = Path("/home/andre/dev_root/robot/yolo_src/datasetss/coco/yolosets")  # 你的数据集根目录
SPLITS = ["train2017", "val2017", "test"]      # 要处理的子集名称（如果验证集叫 val2017，请修改）
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}
LABEL_EXTENSION = ".txt"

# 备份目录（将不匹配的文件移动到这里，而不是删除）
BACKUP_ROOT = DATASET_ROOT / "_dataset_backup_unmatched"
# ==============================

def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)

def get_stem(filename):
    """返回不带扩展名的文件名"""
    return Path(filename).stem

def clean_split(split, dry_run=False):
    """
    清洗单个子集（如 train）
    返回：(matched_count, missing_label_count, orphan_label_count)
    """
    img_dir = DATASET_ROOT / "images" / split
    lbl_dir = DATASET_ROOT / "labels" / split

    if not img_dir.exists() or not lbl_dir.exists():
        print(f"⚠️ 跳过 {split}：images 或 labels 目录不存在")
        return 0, 0, 0

    # 备份目录（按 split 分别存放，便于恢复）
    backup_img_dir = BACKUP_ROOT / "images" / split
    backup_lbl_dir = BACKUP_ROOT / "labels" / split
    if not dry_run:
        ensure_dir(backup_img_dir)
        ensure_dir(backup_lbl_dir)

    # 获取所有图片和标签文件 stem -> 完整路径
    img_files = {f.stem: f for f in img_dir.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS}
    lbl_files = {f.stem: f for f in lbl_dir.iterdir() if f.is_file() and f.suffix.lower() == LABEL_EXTENSION}

    img_stems = set(img_files.keys())
    lbl_stems = set(lbl_files.keys())

    # 需要保留的交集
    keep_stems = img_stems & lbl_stems
    # 需要移除的
    missing_label_stems = img_stems - lbl_stems   # 有图片无标签
    orphan_label_stems = lbl_stems - img_stems    # 有标签无图片

    # 移动缺失标签的图片到 backup
    for stem in missing_label_stems:
        src = img_files[stem]
        dst = backup_img_dir / src.name
        if dry_run:
            print(f"[模拟] 移动图片: {src} -> {dst}")
        else:
            shutil.move(str(src), str(dst))
            print(f"✅ 移动图片: {src} -> {dst}")

    # 移动多余的标签文件到 backup
    for stem in orphan_label_stems:
        src = lbl_files[stem]
        dst = backup_lbl_dir / src.name
        if dry_run:
            print(f"[模拟] 移动标签: {src} -> {dst}")
        else:
            shutil.move(str(src), str(dst))
            print(f"✅ 移动标签: {src} -> {dst}")

    print(f"\n{split} 集清洗完成: 保留 {len(keep_stems)} 对 (图片+标签)")
    print(f"  缺失标签的图片: {len(missing_label_stems)} 已移走")
    print(f"  多余的标签文件: {len(orphan_label_stems)} 已移走")
    return len(keep_stems), len(missing_label_stems), len(orphan_label_stems)

def generate_summary_report(results, output_csv="dataset_clean_report.csv"):
    """生成 CSV 总结报告"""
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["split", "保留对数", "缺失标签的图片数", "多余标签文件数"])
        total_kept = 0
        total_missing = 0
        total_orphan = 0
        for split, (kept, missing, orphan) in results.items():
            writer.writerow([split, kept, missing, orphan])
            total_kept += kept
            total_missing += missing
            total_orphan += orphan
        writer.writerow(["总计", total_kept, total_missing, total_orphan])
    print(f"\n📄 报告已保存至: {output_csv}")

def main():
    print("=" * 60)
    print("数据集清洗：只保留图片与标签成对的样本")
    print("不匹配的文件会被移动到备份目录，不会直接删除")
    print(f"数据集根目录: {DATASET_ROOT.resolve()}")
    print(f"备份目录: {BACKUP_ROOT.resolve()}")
    print("=" * 60)

    # 先 dry-run 预览
    print("\n🔍 模拟运行 (dry-run) 查看将移动哪些文件...")
    results = {}
    for split in SPLITS:
        print(f"\n--- 处理 {split} ---")
        kept, missing, orphan = clean_split(split, dry_run=True)
        results[split] = (kept, missing, orphan)

    print("\n" + "=" * 60)
    answer = input("是否执行实际移动操作？(y/N): ").strip().lower()
    if answer != 'y':
        print("已取消，未修改任何文件。")
        return

    print("\n🚀 开始实际移动...")
    final_results = {}
    for split in SPLITS:
        print(f"\n--- 处理 {split} ---")
        kept, missing, orphan = clean_split(split, dry_run=False)
        final_results[split] = (kept, missing, orphan)

    generate_summary_report(final_results)
    print("\n✅ 清洗完成！原始不匹配的文件已备份到:", BACKUP_ROOT)
    print("   建议检查备份目录，确认无误后可手动删除。")

if __name__ == "__main__":
    main()