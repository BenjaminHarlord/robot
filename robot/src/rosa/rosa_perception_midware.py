import time
from datetime import datetime
from pathlib import Path

try:
    import cv2
except ImportError:
    cv2 = None

_YOLO = None


def _get_yolo():
    global _YOLO
    if _YOLO is None:
        from ultralytics import YOLO as _YOLO
    return _YOLO

QRS_ROOT = Path(__file__).resolve().parent.parent.parent.parent / "QRS"
DEFAULT_MODELS_DIR = QRS_ROOT / "models"
DEFAULT_IMAGES_DIR = QRS_ROOT / "images"

MODEL_VARIANTS = ["yolo26n.pt", "yolo26s.pt", "yolo11n.pt", "yolov8n.pt"]

CONFIDENCE_THRESHOLD = 0.5


class SingleFrameDetection:
    def __init__(self, objects, confidences, annotated_frame, timestamp):
        self.objects = objects
        self.confidences = confidences
        self.annotated_frame = annotated_frame
        self.timestamp = timestamp
        self.count = len(objects)
        self.summary = ", ".join(objects) if objects else "无检测目标"

    def to_dict(self):
        return {
            "objects": self.objects,
            "confidences": self.confidences,
            "count": self.count,
            "summary": self.summary,
            "timestamp": self.timestamp,
        }

    def has_object(self, name):
        return any(name.lower() in obj.lower() for obj in self.objects)

    def __repr__(self):
        return f"<Detection count={self.count} objects={self.summary}>"


class PerceptionMiddleware:
    def __init__(self, model_path=None, confidence_threshold=None,
                 images_dir=None, models_dir=None):
        self._model_path = model_path
        self._confidence_threshold = confidence_threshold or CONFIDENCE_THRESHOLD
        self._images_dir = Path(images_dir) if images_dir else DEFAULT_IMAGES_DIR
        self._models_dir = Path(models_dir) if models_dir else DEFAULT_MODELS_DIR
        self._model = None
        self._last_detection = None

    @property
    def model(self):
        return self._model

    @property
    def is_loaded(self):
        return self._model is not None

    @property
    def model_path(self):
        return self._model_path

    @model_path.setter
    def model_path(self, path):
        self._model_path = path

    @property
    def images_dir(self):
        self._images_dir.mkdir(parents=True, exist_ok=True)
        return self._images_dir

    def load_model(self, model_path=None):
        if model_path:
            self._model_path = model_path
        if not self._model_path:
            found = self._find_default_model()
            if found:
                self._model_path = str(found)
            else:
                raise FileNotFoundError(
                    f"未找到YOLO模型，请在 {self._models_dir} 中放置 .pt 文件或指定 model_path"
                )
        self._model = _get_yolo()(self._model_path)
        return self

    def _find_default_model(self):
        for base in [self._models_dir, Path.cwd() / "yolo_src" / "model"]:
            if not base.exists():
                continue
            for variant in MODEL_VARIANTS:
                candidate = base / variant
                if candidate.exists():
                    return candidate
        return None

    def detect_image(self, image_path):
        if not self.is_loaded:
            self.load_model()
        frame = cv2.imread(image_path)
        if frame is None:
            raise ValueError(f"无法读取图片: {image_path}")
        return self._run_detection(frame)

    def detect_frame(self, frame):
        if not self.is_loaded:
            self.load_model()
        return self._run_detection(frame)

    def capture_single(self, device=0):
        if not self.is_loaded:
            self.load_model()
        cap = cv2.VideoCapture(device)
        if not cap.isOpened():
            raise RuntimeError(f"无法打开摄像头设备: {device}")
        try:
            ret, frame = cap.read()
            if not ret or frame is None:
                raise RuntimeError("无法从摄像头读取画面")
            return self._run_detection(frame)
        finally:
            cap.release()

    def capture_multiple(self, device=0, num_frames=5, interval_sec=0.5):
        results = []
        for i in range(num_frames):
            try:
                results.append(self.capture_single(device))
            except RuntimeError:
                break
            if i < num_frames - 1:
                time.sleep(interval_sec)
        return results

    def _run_detection(self, frame):
        results = self._model(frame, verbose=False)
        result = results[0]

        objects = []
        confidences = []
        if result.boxes is not None:
            for box in result.boxes:
                conf = float(box.conf[0]) if box.conf is not None and len(box.conf) > 0 else 0.0
                if conf < self._confidence_threshold:
                    continue
                cls_id = int(box.cls[0]) if box.cls is not None and len(box.cls) > 0 else -1
                cls_name = self._model.names.get(cls_id, f"cls_{cls_id}")
                objects.append(cls_name)
                confidences.append(round(conf, 4))

        annotated = result.plot()
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        detection = SingleFrameDetection(objects, confidences, annotated, ts)
        self._last_detection = detection
        return detection

    def get_latest_detection(self):
        return self._last_detection

    @property
    def has_recent_detection(self):
        if self._last_detection is None:
            return False
        elapsed = (datetime.now() - datetime.strptime(
            self._last_detection.timestamp.split(".")[0], "%Y-%m-%d %H:%M:%S"
        )).total_seconds()
        return elapsed < 2.0

    def wait_for_detection(self, timeout=3.0):
        start = time.time()
        while time.time() - start < timeout:
            if self._last_detection is not None:
                return self._last_detection
            time.sleep(0.1)
        return None

    def find_object(self, target_name):
        detection = self.capture_single()
        return detection.has_object(target_name)

    def count_objects(self, target_name=None):
        detection = self.capture_single()
        if target_name:
            return sum(1 for obj in detection.objects if target_name.lower() in obj.lower())
        return detection.count

    def list_detected(self):
        detection = self.capture_single()
        return detection.objects

    def save_frame(self, detection, prefix="det"):
        self.images_dir
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{prefix}_{ts}.jpg"
        filepath = self._images_dir / filename
        cv2.imwrite(str(filepath), detection.annotated_frame)
        return filepath

    def __repr__(self):
        return (
            f"<PerceptionMiddleware loaded={self.is_loaded} "
            f"model={Path(self._model_path).name if self._model_path else 'None'}>"
        )
