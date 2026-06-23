import csv
from datetime import datetime
from pathlib import Path

import cv2
from ultralytics import YOLO
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap, QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QMessageBox, QDialog,
    QGroupBox, QSizePolicy
)

TRIGGER_PHRASE = "亲密那有什么，请识别"
YOLO_RECORD_DIR = Path("/home/andre/dev_root/robot/QRP/yolo_record")
CSV_FIELDS = [
    "u_id", "u_na", "u_position",
    "detection_time", "detected_objects", "confidence",
    "frame_path", "model_name"
]
CONFIDENCE_THRESHOLD = 0.5
SAVE_FRAME_INTERVAL = 10


class ModelSelectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("请选择识别模型地址")
        self.setMinimumWidth(520)
        self._model_path = ""
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        hint = QLabel("请选择 YOLO 模型文件 (.pt):")
        hint.setFont(QFont("Microsoft YaHei", 12))
        layout.addWidget(hint)

        file_layout = QHBoxLayout()
        file_layout.setSpacing(8)
        self.path_label = QLabel("未选择文件")
        self.path_label.setStyleSheet(
            "QLabel { background-color: #f5f5f5; padding: 8px; border: 1px solid #ccc; "
            "border-radius: 4px; min-height: 24px; }"
        )
        self.path_label.setWordWrap(True)
        file_layout.addWidget(self.path_label, stretch=1)

        browse_btn = QPushButton("浏览...")
        browse_btn.setMinimumHeight(32)
        browse_btn.clicked.connect(self._browse)
        file_layout.addWidget(browse_btn)
        layout.addLayout(file_layout)

        default_group = QGroupBox("快捷选择默认模型")
        default_layout = QHBoxLayout()
        default_layout.setSpacing(6)
        default_models = [
            ("yolo26n.pt", "Nano"),
            ("yolo26s.pt", "Small"),
            ("yolo26m.pt", "Medium"),
            ("yolo26l.pt", "Large"),
            ("yolo26x.pt", "XLarge"),
        ]
        for model_file, label in default_models:
            btn = QPushButton(label)
            btn.setMinimumHeight(28)
            btn.clicked.connect(lambda checked, m=model_file: self._select_default(m))
            default_layout.addWidget(btn)
        default_group.setLayout(default_layout)
        layout.addWidget(default_group)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("取消")
        cancel_btn.setMinimumHeight(32)
        cancel_btn.setMinimumWidth(80)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("开始检测")
        ok_btn.setMinimumHeight(32)
        ok_btn.setMinimumWidth(100)
        ok_btn.setStyleSheet(
            "QPushButton { background-color: #2e7d32; color: white; border: none; "
            "border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background-color: #1b5e20; }"
        )
        ok_btn.clicked.connect(self._on_ok)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

    def _browse(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 YOLO 模型文件", str(Path.home()), "PT 文件 (*.pt);;所有文件 (*)"
        )
        if file_path:
            self._model_path = file_path
            self.path_label.setText(file_path)

    def _select_default(self, model_name):
        search_paths = [
            Path("/home/andre/dev_root/robot/robot/src/model") / model_name,
            Path.cwd() / model_name,
            Path.home() / "dev_root" / "robot" / "robot" / "src" / "model" / model_name,
        ]
        for p in search_paths:
            if p.exists():
                self._model_path = str(p)
                self.path_label.setText(str(p))
                return
        self.path_label.setText(f"未找到: {model_name} (请手动浏览)")

    def _on_ok(self):
        if not self._model_path or not Path(self._model_path).exists():
            QMessageBox.warning(self, "警告", "请先选择一个有效的模型文件")
            return
        if not self._model_path.endswith(".pt"):
            QMessageBox.warning(self, "警告", "请选择 .pt 格式的模型文件")
            return
        self.accept()

    def get_model_path(self):
        return self._model_path


class DetectionWorker(QThread):
    frame_ready = pyqtSignal(QPixmap, dict)
    error_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, model_path, device=0):
        super().__init__()
        self.model_path = model_path
        self.device = device
        self._running = True
        self.model = None
        self.cap = None
        self.record_dir = YOLO_RECORD_DIR

    def run(self):
        try:
            self.model = YOLO(self.model_path)
            self.cap = cv2.VideoCapture(self.device)
            if not self.cap.isOpened():
                self.error_signal.emit(f"无法打开摄像头设备: {self.device}")
                return

            self.record_dir.mkdir(parents=True, exist_ok=True)
            frame_count = 0

            while self._running:
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    self.msleep(50)
                    continue

                results = self.model(frame, verbose=False)
                annotated = results[0].plot()
                detection_info = self._extract_detection(results[0])

                if frame_count % SAVE_FRAME_INTERVAL == 0 and detection_info["objects"]:
                    self._save_record(detection_info, annotated)

                rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb.shape
                qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg).copy()

                self.frame_ready.emit(pixmap, detection_info)
                frame_count += 1
                self.msleep(33)

        except Exception as e:
            self.error_signal.emit(f"检测异常: {str(e)}")
        finally:
            if self.cap is not None:
                self.cap.release()
            self.finished_signal.emit()

    def _extract_detection(self, result):
        objects = []
        confidences = []
        if result.boxes is not None:
            for box in result.boxes:
                conf = float(box.conf[0]) if box.conf is not None and len(box.conf) > 0 else 0.0
                if conf < CONFIDENCE_THRESHOLD:
                    continue
                cls_id = int(box.cls[0]) if box.cls is not None and len(box.cls) > 0 else -1
                cls_name = self.model.names.get(cls_id, f"cls_{cls_id}")
                objects.append(cls_name)
                confidences.append(conf)
        return {
            "objects": objects,
            "confidences": confidences,
            "count": len(objects),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "summary": ", ".join(objects) if objects else "无检测目标",
        }

    def _save_record(self, detection_info, annotated_frame):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        frame_dir = self.record_dir / "frames"
        frame_dir.mkdir(parents=True, exist_ok=True)
        frame_filename = f"det_{ts}.jpg"
        frame_path = frame_dir / frame_filename
        cv2.imwrite(str(frame_path), annotated_frame)

        csv_path = self._get_csv_path()
        file_exists = csv_path.exists()
        row = {
            "u_id": "",
            "u_na": "",
            "u_position": "",
            "detection_time": detection_info["time"],
            "detected_objects": detection_info["summary"],
            "confidence": str([round(c, 4) for c in detection_info["confidences"]]),
            "frame_path": str(frame_path),
            "model_name": Path(self.model_path).name,
        }
        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

    def _get_csv_path(self):
        today = datetime.now().strftime("%y%m%d")
        return self.record_dir / f"{today}.csv"

    def stop(self):
        self._running = False


class DetectionPanel(QWidget):
    stop_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.model_path = ""
        self.setMinimumWidth(280)
        self.setMaximumWidth(420)
        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding
        )
        self._init_ui()
        self.setVisible(False)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        title = QLabel("YOLO 实时检测")
        title.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "QLabel { padding: 4px; background-color: #1b5e20; color: white; "
            "border-radius: 4px; }"
        )
        layout.addWidget(title)

        self.video_label = QLabel("等待启动...")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumHeight(200)
        self.video_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.video_label.setStyleSheet(
            "QLabel { background-color: #1a1a1a; color: #888; border: 2px solid #444; "
            "border-radius: 4px; }"
        )
        layout.addWidget(self.video_label, stretch=1)

        info_frame = QGroupBox("检测信息")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(4)

        self.info_label = QLabel("等待检测...")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("QLabel { color: #333; font-size: 10pt; }")
        info_layout.addWidget(self.info_label)

        self.count_label = QLabel("数量: 0")
        self.count_label.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        self.count_label.setStyleSheet("QLabel { color: #e65100; font-size: 11pt; }")
        info_layout.addWidget(self.count_label)

        self.model_label = QLabel("模型: --")
        self.model_label.setStyleSheet("QLabel { color: #666; font-size: 9pt; }")
        info_layout.addWidget(self.model_label)

        layout.addWidget(info_frame)

        self.stop_btn = QPushButton("停止检测")
        self.stop_btn.setMinimumHeight(30)
        self.stop_btn.setStyleSheet(
            "QPushButton { background-color: #c62828; color: white; border: none; "
            "border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background-color: #b71c1c; }"
        )
        self.stop_btn.clicked.connect(self._on_stop)
        layout.addWidget(self.stop_btn)

    def start(self, model_path, device=0):
        self.model_path = model_path
        self.model_label.setText(f"模型: {Path(model_path).name}")
        self.setVisible(True)

        self.worker = DetectionWorker(model_path, device)
        self.worker.frame_ready.connect(self._on_frame)
        self.worker.error_signal.connect(self._on_error)
        self.worker.finished_signal.connect(self._on_finished)
        self.worker.start()

    def _on_frame(self, pixmap, info):
        panel_w = self.video_label.width()
        panel_h = self.video_label.height()
        if panel_w > 10 and panel_h > 10:
            scaled = pixmap.scaled(
                panel_w, panel_h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        else:
            scaled = pixmap.scaled(
                280, 200,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        self.video_label.setPixmap(scaled)
        self.info_label.setText(f"检测目标: {info['summary']}")
        self.count_label.setText(f"数量: {info['count']}")

    def _on_error(self, msg):
        self.video_label.setText(f"错误: {msg}")
        self.info_label.setText("检测出错，请重试")

    def _on_finished(self):
        self.video_label.setText("检测已停止")
        self.setVisible(False)
        self.stop_requested.emit()

    def _on_stop(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(3000)
        self.setVisible(False)
        self.stop_requested.emit()

    def shutdown(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(3000)

    def is_running(self):
        return self.worker is not None and self.worker.isRunning()


class YOLOSkill:
    TRIGGER_PHRASE = TRIGGER_PHRASE
    YOLO_RECORD_DIR = YOLO_RECORD_DIR

    def __init__(self):
        self._panel = None

    def is_triggered(self, text):
        return self.TRIGGER_PHRASE in text

    def create_panel(self, parent=None):
        self._panel = DetectionPanel(parent)
        self._panel.stop_requested.connect(self._on_panel_stop)
        return self._panel

    def show_model_dialog(self, parent=None):
        dialog = ModelSelectDialog(parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_model_path()
        return None

    def start_detection(self, model_path, parent=None):
        if self._panel is None:
            self._panel = DetectionPanel(parent)
        self._panel.start(model_path)
        return self._panel

    def stop_detection(self):
        if self._panel and self._panel.is_running():
            self._panel.shutdown()

    def is_running(self):
        return self._panel is not None and self._panel.is_running()

    def _on_panel_stop(self):
        pass

    def get_latest_records(self, limit=10):
        csv_dir = YOLO_RECORD_DIR
        if not csv_dir.exists():
            return []
        csv_files = sorted(csv_dir.glob("*.csv"), reverse=True)
        records = []
        for fp in csv_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        records.append(row)
                        if len(records) >= limit:
                            return records
            except Exception:
                continue
        return records
