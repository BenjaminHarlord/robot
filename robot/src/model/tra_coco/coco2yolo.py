import json
import shutil
import sys
import zipfile
from pathlib import Path
from ultralytics.data.converter import convert_coco

ROOT = Path(__file__).resolve().parent.parent.parent  # yolo_src/
sys.path.insert(0, str(ROOT / "model" / "url_tool" / "ultralytics"))

COCO_ROOT = ROOT / "datasetss" / "coco" / "cocosets"
YOLO_ROOT = ROOT / "datasetss" / "coco" / "yolosets"

ANNOTATIONS_DIR = COCO_ROOT / "annotations_trainval2017" / "annotations"
TRAIN_IMG_DIR = COCO_ROOT / "tr" / "train2017" / "train2017"
VAL_IMG_DIR = COCO_ROOT / "val" / "val2017" / "val2017"
TEST_IMG_DIR = COCO_ROOT / "test" / "test2017" / "test2017"

YOLO_IMAGES_TRAIN = YOLO_ROOT / "images" / "train"
YOLO_IMAGES_VAL = YOLO_ROOT / "images" / "val"
YOLO_IMAGES_TEST = YOLO_ROOT / "images" / "test"
YOLO_LABELS_TRAIN = YOLO_ROOT / "labels" / "train"
YOLO_LABELS_VAL = YOLO_ROOT / "labels" / "val"

COCO80_NAMES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
    "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
    "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack",
    "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball",
    "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket",
    "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
    "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair",
    "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator",
    "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush",
]

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


EXTRACT_DIRS = {
    COCO_ROOT / "annotations_trainval2017.zip": ANNOTATIONS_DIR.parent,
    COCO_ROOT / "tr" / "train2017.zip": TRAIN_IMG_DIR.parent,
    COCO_ROOT / "val" / "val2017.zip": VAL_IMG_DIR.parent,
    COCO_ROOT / "test" / "test2017.zip": TEST_IMG_DIR.parent,
}


def step0_extract_zips():
    print("[0/5] Extracting COCO zip files...")
    for zip_path, dest_dir in EXTRACT_DIRS.items():
        if not zip_path.exists():
            print(f"    WARNING: {zip_path} not found, skipping.")
            continue
        if dest_dir.exists():
            print(f"    Skipping {zip_path.name}, already extracted.")
            continue
        print(f"    Extracting {zip_path.name} → {dest_dir} ...")
        dest_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(dest_dir)
        print(f"    Done.")
    print("    All zips extracted.\n")


def step1_convert_labels():
    print("[1/5] Converting COCO JSON annotations to YOLO .txt labels...")
    import tempfile

    if YOLO_ROOT.exists():
        shutil.rmtree(YOLO_ROOT, ignore_errors=True)
    for p in YOLO_ROOT.parent.glob(f"{YOLO_ROOT.name}-*"):
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)

    tmp_dir = Path(tempfile.mkdtemp())
    for f in ANNOTATIONS_DIR.glob("instances_*.json"):
        shutil.copy2(f, tmp_dir / f.name)

    try:
        convert_coco(
            labels_dir=str(tmp_dir),
            save_dir=str(YOLO_ROOT),
            use_segments=False,
            use_keypoints=False,
            cls91to80=True,
        )
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    # `increment_path` inside convert_coco may create numbered dirs instead.
    # Find the actual output dir that has labels/ inside it.
    actual_root = YOLO_ROOT
    if not actual_root.exists():
        candidates = sorted(
            YOLO_ROOT.parent.glob(f"{YOLO_ROOT.name}-*"),
            key=lambda p: p.stat().st_ctime, reverse=True,
        )
        if candidates:
            actual_root = candidates[0]
            # Rename back to expected YOLO_ROOT
            shutil.rmtree(YOLO_ROOT, ignore_errors=True)
            shutil.move(str(actual_root), str(YOLO_ROOT))
        else:
            raise FileNotFoundError(
                f"convert_coco did not create expected directory: {YOLO_ROOT}"
            )

    print("    Done.")


def step2_organize_labels():
    print("[2/5] Organizing label files into labels/train and labels/val...")
    labels_root = YOLO_ROOT / "labels"

    source_train = labels_root / "train2017"
    source_val = labels_root / "val2017"

    if not source_train.exists():
        raise FileNotFoundError(f"Label dir not found: {source_train}")
    if not source_val.exists():
        raise FileNotFoundError(f"Label dir not found: {source_val}")

    YOLO_LABELS_TRAIN.mkdir(parents=True, exist_ok=True)
    YOLO_LABELS_VAL.mkdir(parents=True, exist_ok=True)

    train_count = 0
    for f in source_train.glob("*.txt"):
        shutil.move(str(f), str(YOLO_LABELS_TRAIN / f.name))
        train_count += 1

    val_count = 0
    for f in source_val.glob("*.txt"):
        shutil.move(str(f), str(YOLO_LABELS_VAL / f.name))
        val_count += 1

    for leftover in labels_root.iterdir():
        if leftover.is_dir() and leftover.name not in ("train", "val"):
            shutil.rmtree(leftover, ignore_errors=True)

    print(f"    Train labels: {train_count}")
    print(f"    Val labels:   {val_count}")
    print("    Done.")
    return train_count, val_count


def step3_copy_images():
    print("[3/5] Copying images to yolosets/images/ (train / val / test)...")

    YOLO_IMAGES_TRAIN.mkdir(parents=True, exist_ok=True)
    YOLO_IMAGES_VAL.mkdir(parents=True, exist_ok=True)
    YOLO_IMAGES_TEST.mkdir(parents=True, exist_ok=True)

    def copy_images(src_dir, dst_dir):
        imgs = [p for p in src_dir.glob("*") if p.suffix.lower() in IMG_EXTS]
        for img in imgs:
            dst = dst_dir / img.name
            if not dst.exists():
                shutil.copy2(img, dst)
        return len(imgs)

    n_train = copy_images(TRAIN_IMG_DIR, YOLO_IMAGES_TRAIN)
    n_val = copy_images(VAL_IMG_DIR, YOLO_IMAGES_VAL)
    n_test = copy_images(TEST_IMG_DIR, YOLO_IMAGES_TEST)

    print(f"    Train images: {n_train}")
    print(f"    Val images:   {n_val}")
    print(f"    Test images:  {n_test}")
    print("    Done.")
    return n_train, n_val, n_test


def step4_verify():
    print("[4/5] Verifying image-label correspondence...")

    train_imgs = {p.stem for p in YOLO_IMAGES_TRAIN.glob("*") if p.suffix.lower() in IMG_EXTS}
    train_labels = {p.stem for p in YOLO_LABELS_TRAIN.glob("*.txt")}
    val_imgs = {p.stem for p in YOLO_IMAGES_VAL.glob("*") if p.suffix.lower() in IMG_EXTS}
    val_labels = {p.stem for p in YOLO_LABELS_VAL.glob("*.txt")}

    train_no_label = train_imgs - train_labels
    train_no_img = train_labels - train_imgs
    if train_no_label:
        print(f"    WARNING: {len(train_no_label)} train images have no label")
    if train_no_img:
        print(f"    WARNING: {len(train_no_img)} train labels have no image")

    val_no_label = val_imgs - val_labels
    val_no_img = val_labels - val_imgs
    if val_no_label:
        print(f"    WARNING: {len(val_no_label)} val images have no label")
    if val_no_img:
        print(f"    WARNING: {len(val_no_img)} val labels have no image")

    print("    Done.")


def step5_create_yaml():
    print("[5/5] Creating data.yaml...")
    yaml_path = YOLO_ROOT / "data.yaml"

    names_block = "\n".join(f"  {i}: {name}" for i, name in enumerate(COCO80_NAMES))

    yaml_content = (
        f"# YOLO dataset config — COCO 2017 converted\n"
        f"# Auto-generated by src/model/tra_coco/coco2yolo.py\n"
        f"# Use: yolo train data={yaml_path.as_posix()}\n\n"
        f"path: {YOLO_ROOT.as_posix()}\n"
        f"train: images/train\n"
        f"val: images/val\n"
        f"test: images/test\n\n"
        f"nc: 80\n"
        f"names:\n{names_block}\n"
    )

    yaml_path.write_text(yaml_content, encoding="utf-8")
    print(f"    data.yaml → {yaml_path}")


def main():
    print("=" * 60)
    print("  COCO 2017 → YOLO Dataset Conversion")
    print(f"  Annotations : {ANNOTATIONS_DIR}")
    print(f"  Train images: {TRAIN_IMG_DIR}")
    print(f"  Val images  : {VAL_IMG_DIR}")
    print(f"  Test images : {TEST_IMG_DIR}")
    print(f"  Output      : {YOLO_ROOT}")
    print("=" * 60)

    step0_extract_zips()
    step1_convert_labels()
    step2_organize_labels()
    step3_copy_images()
    step4_verify()
    step5_create_yaml()

    # Summary
    train_imgs = len(list(YOLO_IMAGES_TRAIN.glob("*")))
    val_imgs = len(list(YOLO_IMAGES_VAL.glob("*")))
    test_imgs = len(list(YOLO_IMAGES_TEST.glob("*")))
    train_lbls = len(list(YOLO_LABELS_TRAIN.glob("*.txt")))
    val_lbls = len(list(YOLO_LABELS_VAL.glob("*.txt")))

    print("\n" + "=" * 60)
    print("  SUMMARY")
    print(f"  train : {train_imgs} images, {train_lbls} labels")
    print(f"  val   : {val_imgs} images, {val_lbls} labels")
    print(f"  test  : {test_imgs} images (no labels, COCO test-dev)")
    print(f"  nc=80 | data.yaml={YOLO_ROOT / 'data.yaml'}")
    print("=" * 60)
    print()
    print("  Train with:")
    print(f"  yolo train model=yolo11n.pt data={YOLO_ROOT.as_posix()}/data.yaml epochs=300 imgsz=640")
    print()


if __name__ == "__main__":
    main()
