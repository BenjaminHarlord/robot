import json
import re
import sys
from pathlib import Path

import cv2
from PyQt6.QtCore import Qt, QEvent, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor, QImage, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QTextBrowser, QPushButton, QLabel, QLineEdit, QDialog,
    QDialogButtonBox, QFormLayout, QMessageBox, QComboBox,
    QGroupBox, QSizePolicy, QFrame, QFileDialog,
)

SRC_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SRC_DIR))

from rosa import ROSAAgent
from rosa.rosa_decision_midware import ActionType

COLOR_USER = "#16a085"
COLOR_REPLY = "#e65100"
COLOR_SYSTEM = "#ffffff"
COLOR_RED = "#c62828"

_MD_IMG_RE = re.compile(r'!\[([^\]]*)\]\(([^)\s]+)\)')
_MD_LINK_RE = re.compile(r'(?<!\!)\[([^\]]+)\]\(([^)\s]+)\)')
_MD_BOLD_RE = re.compile(r'\*\*(.+?)\*\*')
_MD_ITALIC_RE = re.compile(r'\*(.+?)\*')
_MD_CODE_INLINE_RE = re.compile(r'`([^`]+)`')
_MD_CODE_BLOCK_RE = re.compile(r'```(\w*)\n?(.*?)```', re.DOTALL)


def md_to_html(text):
    buf = text
    blocks = []
    last = 0
    for m in _MD_CODE_BLOCK_RE.finditer(buf):
        blocks.append(("text", buf[last:m.start()]))
        code = m.group(2)
        code_escaped = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        blocks.append(("code", f'<pre style="background:#2d2d2d;color:#f8f8f2;padding:12px;'
                                f'border-radius:6px;overflow-x:auto;font-family:monospace;'
                                f'font-size:9pt;margin:8px 0;line-height:1.4;">'
                                f'{code_escaped}</pre>'))
        last = m.end()
    blocks.append(("text", buf[last:]))

    result_parts = []
    for kind, part in blocks:
        if kind == "code":
            result_parts.append(part)
        else:
            part = _MD_IMG_RE.sub(
                lambda m: (f'<br><img src="{m.group(2)}" alt="{m.group(1)}" '
                           f'style="max-width:480px;max-height:360px;border-radius:6px;'
                           f'margin:8px 0;display:block;"><br>'),
                part)
            part = _MD_LINK_RE.sub(r'<a href="\2" style="color:{0};">\1</a>'.format(COLOR_SYSTEM), part)
            part = _MD_BOLD_RE.sub(r'<b>\1</b>', part)
            part = _MD_ITALIC_RE.sub(r'<i>\1</i>', part)
            part = _MD_CODE_INLINE_RE.sub(
                r'<code style="background:#f0f0f0;padding:2px 5px;border-radius:3px;'
                r'font-family:monospace;font-size:9pt;">\1</code>', part)
            lines = part.split("\n")
            for i, line in enumerate(lines):
                if line.startswith("### "):
                    lines[i] = f'<h4 style="margin:6px 0 2px 0;">{line[4:]}</h4>'
                elif line.startswith("## "):
                    lines[i] = f'<h3 style="margin:8px 0 2px 0;">{line[3:]}</h3>'
                elif line.startswith("# "):
                    lines[i] = f'<h2 style="margin:10px 0 2px 0;">{line[2:]}</h2>'
                elif re.match(r'^\d+\.\s', line):
                    lines[i] = f'<div style="margin-left:16px;">{line}</div>'
                elif line.startswith("- "):
                    lines[i] = f'<div style="margin-left:16px;">&#8226; {line[2:]}</div>'
            part = "<br>".join(lines)
            result_parts.append(part)
    return "".join(result_parts)


class ROSAProcessWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, agent, user_text):
        super().__init__()
        self.agent = agent
        self.text = user_text

    def run(self):
        try:
            result = self.agent.process(self.text)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class ROSAStreamWorker(QThread):
    chunk = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, agent, message):
        super().__init__()
        self.agent = agent
        self.message = message

    def run(self):
        try:
            full = self.agent.chat_reply_stream(
                self.message,
                chunk_callback=lambda c: self.chunk.emit(c),
            )
            self.finished.emit(full)
        except Exception as e:
            self.error.emit(str(e))


class ROSADetectWorker(QThread):
    frame_ready = pyqtSignal(QPixmap, dict)
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, agent, model_path, confidence_threshold=0.5, device=0):
        super().__init__()
        self.agent = agent
        self._model_path = model_path
        self._confidence = confidence_threshold
        self._device = device
        self._running = True
        self._latest_detection = None

    @property
    def latest_detection(self):
        return self._latest_detection

    def run(self):
        try:
            self.agent.perception.load_model(self._model_path)

            cap = cv2.VideoCapture(self._device)
            if not cap.isOpened():
                self.error.emit(f"无法打开摄像头设备: {self._device}")
                return

            while self._running:
                ret, frame = cap.read()
                if not ret or frame is None:
                    self.msleep(50)
                    continue

                detection = self.agent.perception.detect_frame(frame)
                self._latest_detection = detection

                rgb = cv2.cvtColor(detection.annotated_frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb.shape
                qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg).copy()

                self.frame_ready.emit(pixmap, detection.to_dict())
                self.msleep(33)

            cap.release()
        except Exception as e:
            self.error.emit(f"检测异常: {str(e)}")
        finally:
            self.finished.emit()

    def stop(self):
        self._running = False


class ROSADetectPanel(QWidget):
    stop_requested = pyqtSignal()

    def __init__(self, agent, parent=None):
        super().__init__(parent)
        self.agent = agent
        self._worker = None
        self._last_info = None
        self._last_pixmap = None
        self._stopped = False
        self.setMinimumWidth(280)
        self.setMaximumWidth(420)
        self._init_ui()

    def is_running(self):
        return self._worker is not None and self._worker.isRunning()

    def get_latest_info(self):
        return self._last_info

    def get_latest_pixmap(self):
        return self._last_pixmap

    @property
    def detect_worker(self):
        return self._worker

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        title = QLabel("实时检测")
        title.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            f"QLabel {{ padding: 4px; background-color: {COLOR_SYSTEM}; color: white; border-radius: 4px; }}"
        )
        layout.addWidget(title)

        self.video_label = QLabel("等待启动...")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumHeight(200)
        self.video_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.video_label.setStyleSheet(
            "QLabel { background-color: #1a1a1a; color: #90caf9; border: 2px solid #444; border-radius: 4px; }"
        )
        layout.addWidget(self.video_label, stretch=1)

        info_frame = QGroupBox("检测信息")
        info_frame.setStyleSheet(
            f"QGroupBox {{ color: {COLOR_SYSTEM}; font-weight: bold; }}"
        )
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(4)

        self.info_label = QLabel("等待检测...")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("QLabel { color: #333; font-size: 10pt; }")
        info_layout.addWidget(self.info_label)

        self.count_label = QLabel("数量: 0")
        self.count_label.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        self.count_label.setStyleSheet(f"QLabel {{ color: {COLOR_REPLY}; font-size: 11pt; }}")
        info_layout.addWidget(self.count_label)

        self.model_label = QLabel("模型: --")
        self.model_label.setStyleSheet(f"QLabel {{ color: {COLOR_SYSTEM}; font-size: 9pt; }}")
        info_layout.addWidget(self.model_label)

        layout.addWidget(info_frame)

        self.stop_btn = QPushButton("停止检测")
        self.stop_btn.setMinimumHeight(32)
        self.stop_btn.setStyleSheet(
            f"QPushButton {{ background-color: {COLOR_RED}; color: white; border: none; "
            "border-radius: 4px; font-weight: bold; font-size: 11pt; }"
            "QPushButton:hover { background-color: #b71c1c; }"
        )
        self.stop_btn.clicked.connect(self._on_stop)
        layout.addWidget(self.stop_btn)

    def start(self, model_path):
        self._stopped = False
        self.model_label.setText(f"模型: {Path(model_path).name}")
        self.show()

        self._worker = ROSADetectWorker(
            self.agent,
            model_path=model_path,
            confidence_threshold=self.agent.config.get(
                "perception", "confidence_threshold", default=0.5
            ),
        )
        self._worker.frame_ready.connect(self._on_frame)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_frame(self, pixmap, info):
        self._last_pixmap = pixmap
        self._last_info = info

        pw = self.video_label.width()
        ph = self.video_label.height()
        if pw > 10 and ph > 10:
            scaled = pixmap.scaled(
                pw, ph, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        else:
            scaled = pixmap.scaled(
                280, 200, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        self.video_label.setPixmap(scaled)
        self.info_label.setText(f"检测目标: {info.get('summary', '')}")
        self.count_label.setText(f"数量: {info.get('count', 0)}")

    def _on_error(self, msg):
        self.video_label.setText(f"错误: {msg}")
        self.info_label.setText("检测出错，请重试")

    def _on_finished(self):
        self.video_label.setText("检测已停止")
        self._emit_stop_once()

    def _on_stop(self):
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait(3000)
        self._emit_stop_once()

    def _emit_stop_once(self):
        if not self._stopped:
            self._stopped = True
            self.stop_requested.emit()

    def shutdown(self):
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait(3000)


class ApiKeyDialog(QDialog):
    def __init__(self, current_key="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置 API Key")
        self.setMinimumWidth(450)
        layout = QFormLayout(self)
        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setText(current_key)
        self.key_input.setPlaceholderText("输入你的 DeepSeek API Key")
        layout.addRow("API Key:", self.key_input)
        hint = QLabel(
            f'<a href="https://platform.deepseek.com/api_keys" style="color:{COLOR_SYSTEM};">'
            '前往 platform.deepseek.com 获取 API Key</a>'
        )
        hint.setOpenExternalLinks(True)
        layout.addRow("", hint)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_api_key(self):
        return self.key_input.text().strip()


class ModelSelectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择 YOLO 模型")
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
        self.path_label = QLabel("未选择文件")
        self.path_label.setStyleSheet(
            "QLabel { background-color: #f5f5f5; padding: 8px; border: 1px solid #ccc; "
            "border-radius: 4px; min-height: 24px; }"
        )
        self.path_label.setWordWrap(True)
        file_layout.addWidget(self.path_label, stretch=1)

        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self._browse)
        file_layout.addWidget(browse_btn)
        layout.addLayout(file_layout)

        default_group = QGroupBox("快捷选择默认模型")
        default_layout = QHBoxLayout()
        for model_file, label in [
            ("yolo26n.pt", "Nano"), ("yolo26s.pt", "Small"),
            ("yolo26m.pt", "Medium"), ("yolo26l.pt", "Large"),
            ("yolo26x.pt", "XLarge"),
        ]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, m=model_file: self._select_default(m))
            default_layout.addWidget(btn)
        default_group.setLayout(default_layout)
        layout.addWidget(default_group)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        ok_btn = QPushButton("确认选择")
        ok_btn.setStyleSheet(
            f"QPushButton {{ background-color: {COLOR_SYSTEM}; color: white; border: none; "
            "border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background-color: #0d47a1; }"
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
            Path.cwd().parent / "QRS" / "models" / model_name,
            Path(__file__).resolve().parent.parent.parent.parent / "QRS" / "models" / model_name,
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
        self.accept()

    def get_model_path(self):
        return self._model_path


class ROSAWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.agent = None
        self._process_worker = None
        self._stream_worker = None
        self._stream_buffer = ""
        self._stream_anchor = None
        self._messages = []
        self._detect_panel = None
        self._init_agent()
        self.init_ui()

    def _init_agent(self):
        try:
            self.agent = ROSAAgent()
        except Exception:
            self.agent = ROSAAgent.__new__(ROSAAgent)

    def init_ui(self):
        self.setWindowTitle("ROSA 智能体 — 机器人操作系统智能体")
        self.setGeometry(120, 80, 1280, 720)

        central = QWidget()
        self.setCentralWidget(central)
        main_split = QHBoxLayout(central)
        main_split.setContentsMargins(4, 4, 4, 4)
        main_split.setSpacing(6)

        chat_wrapper = QWidget()
        chat_layout = QVBoxLayout(chat_wrapper)
        chat_layout.setSpacing(8)
        chat_layout.setContentsMargins(0, 0, 0, 0)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.addWidget(QLabel("模型:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["deepseek-v4-flash", "deepseek-v4-pro"])
        self.model_combo.setToolTip("选择对话模型")
        controls_layout.addWidget(self.model_combo)
        controls_layout.addStretch()
        chat_layout.addLayout(controls_layout)

        self.chat_display = QTextBrowser()
        self.chat_display.setReadOnly(True)
        self.chat_display.setOpenExternalLinks(True)
        self.chat_display.setStyleSheet(
            "QTextEdit { background-color: #ffffff; color: #1a1a1a; "
            "border: 1px solid #aaa; border-radius: 4px; padding: 8px; }"
        )
        self.chat_display.setFont(QFont("Microsoft YaHei", 12))
        chat_layout.addWidget(self.chat_display, stretch=1)

        decision_frame = QFrame()
        decision_frame.setMaximumHeight(56)
        decision_frame.setStyleSheet(
            f"QFrame {{ background-color: #e3f2fd; "
            f"border: 1px solid #90caf9; border-radius: 4px; padding: 4px; }}"
        )
        decision_layout = QHBoxLayout(decision_frame)
        decision_layout.setContentsMargins(8, 2, 8, 2)
        self.decision_label = QLabel("决策: 等待输入...")
        self.decision_label.setFont(QFont("Microsoft YaHei", 9))
        self.decision_label.setStyleSheet(f"color: {COLOR_SYSTEM};")
        decision_layout.addWidget(self.decision_label)
        chat_layout.addWidget(decision_frame)

        input_layout = QHBoxLayout()
        input_layout.setSpacing(6)
        self.input_field = QTextEdit()
        self.input_field.setMaximumHeight(100)
        self.input_field.setMinimumHeight(50)
        self.input_field.setPlaceholderText("输入消息或指令，按 Enter 发送，Ctrl+Enter 换行...")
        self.input_field.setFont(QFont("Microsoft YaHei", 12))
        self.input_field.setStyleSheet(
            "QTextEdit { border: 1px solid #aaa; border-radius: 4px; padding: 6px; }"
        )
        self.input_field.installEventFilter(self)
        input_layout.addWidget(self.input_field, stretch=1)

        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(4)
        self.send_btn = QPushButton("发送")
        self.send_btn.setMinimumHeight(28)
        self.send_btn.setStyleSheet(
            f"QPushButton {{ background-color: {COLOR_SYSTEM}; color: white; border: none; "
            "border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background-color: #0d47a1; }"
            "QPushButton:disabled { background-color: #aaa; }"
        )
        self.send_btn.clicked.connect(self.send_message)
        btn_layout.addWidget(self.send_btn)
        self.clear_btn = QPushButton("清屏")
        self.clear_btn.setMinimumHeight(28)
        self.clear_btn.clicked.connect(self.clear_chat)
        btn_layout.addWidget(self.clear_btn)
        input_layout.addLayout(btn_layout)
        chat_layout.addLayout(input_layout)

        main_split.addWidget(chat_wrapper, stretch=1)

        self._detect_panel = ROSADetectPanel(self.agent, self)
        self._detect_panel.stop_requested.connect(self._on_detect_stop)
        main_split.addWidget(self._detect_panel)

        status = "就绪" if self.agent and self.agent.llm.is_configured else "就绪 | 请先设置 API Key"
        self.statusBar().showMessage(status)

        menubar = self.menuBar()
        settings_menu = menubar.addMenu("设置")
        apikey_action = settings_menu.addAction("设置 API Key")
        apikey_action.triggered.connect(self.show_api_key_dialog)
        detect_menu = menubar.addMenu("检测")
        start_detect = detect_menu.addAction("启动实时检测")
        start_detect.triggered.connect(self._start_detection)
        stop_detect = detect_menu.addAction("停止实时检测")
        stop_detect.triggered.connect(self._on_detect_stop)
        tools_menu = menubar.addMenu("工具")
        show_data = tools_menu.addAction("查看数据记录")
        show_data.triggered.connect(self._show_data_records)
        show_config = tools_menu.addAction("查看当前配置")
        show_config.triggered.connect(self._show_config)

    def eventFilter(self, obj, event):
        if obj is self.input_field and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return:
                if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                    return False
                self.send_message()
                return True
        return super().eventFilter(obj, event)

    def show_api_key_dialog(self):
        current = self.agent.llm.api_key if self.agent else ""
        dialog = ApiKeyDialog(current, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            key = dialog.get_api_key()
            if key and self.agent:
                self.agent.set_api_key(key)
                self.statusBar().showMessage("API Key 已设置")
            elif self.agent:
                self.agent.llm.api_key = ""
                self.statusBar().showMessage("API Key 已清除")

    def _start_detection(self):
        if self._detect_panel and self._detect_panel.is_running():
            QMessageBox.information(self, "提示", "实时检测已在运行中")
            return

        dialog = ModelSelectDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        model_path = dialog.get_model_path()
        if not model_path:
            return

        self.agent.config.set("perception", "model_path", value=model_path)
        self.append_message("系统",
            f"YOLO 实时检测已启动\n模型: {Path(model_path).name}",
            COLOR_SYSTEM)
        self._detect_panel.start(model_path)
        self.statusBar().showMessage(f"实时检测运行中 — {Path(model_path).name}")

    def _on_detect_stop(self):
        if self._detect_panel:
            self._detect_panel.shutdown()
        self.append_message("系统", "实时检测已停止", "#666")
        self.statusBar().showMessage("就绪")

    def send_message(self):
        text = self.input_field.toPlainText().strip()
        if not text:
            return

        if not self.agent:
            QMessageBox.warning(self, "错误", "Agent 未初始化")
            return

        if not self.agent.llm.is_configured:
            self.show_api_key_dialog()
            if not self.agent.llm.is_configured:
                return

        if self._process_worker and self._process_worker.isRunning():
            QMessageBox.information(self, "提示", "请等待上一个任务完成")
            return

        self.input_field.clear()
        self.send_btn.setEnabled(False)
        self.statusBar().showMessage("ROSA 智能体思考中...")

        self.append_message("你", text, COLOR_USER)

        self._process_worker = ROSAProcessWorker(self.agent, text)
        self._process_worker.finished.connect(self._on_process_result)
        self._process_worker.error.connect(self._on_process_error)
        self._process_worker.start()

    def _on_process_result(self, result):
        self._process_worker = None
        if not result.get("success"):
            self.append_message("ROSA", result.get("message", "处理失败"), COLOR_RED)
            self.send_btn.setEnabled(True)
            self.statusBar().showMessage("就绪")
            return

        decision = result.get("decision", {})
        res = result.get("result", {})
        action = decision.get("action", "")

        self.decision_label.setText(
            f"决策: {action} | 目标: {decision.get('target', '-')} | "
            f"理由: {decision.get('reasoning', '-')}"
        )

        if action == "do_detect":
            self._handle_detect_result(result)
        elif action == "count_objects":
            self.append_message("ROSA", res.get("message", ""), COLOR_REPLY)
        elif action == "check_presence":
            exists = res.get("exists", False)
            self.append_message("ROSA", res.get("message", ""),
                                COLOR_USER if exists else "#333333")
        elif action == "query_history":
            self.append_message("ROSA", f"历史检测记录: {res.get('count', 0)} 条", COLOR_SYSTEM)
        elif action == "chat_reply":
            reply = res.get("reply", "")
            if reply:
                self.append_message("ROSA", reply, COLOR_REPLY)
            else:
                self._stream_chat(result.get("command", {}).get("raw_text", ""))
        elif action == "report_result":
            self.append_message("ROSA",
                json.dumps(res.get("result", {}), ensure_ascii=False, indent=2), "#333")
        else:
            self.append_message("ROSA", res.get("message", str(res)[:200]), "#666")

        self.send_btn.setEnabled(True)
        self.statusBar().showMessage("就绪")

    def _handle_detect_result(self, result):
        res = result.get("result", {})
        cmd = result.get("command", {})

        if res.get("error"):
            if self._detect_panel and self._detect_panel.is_running():
                info = self._detect_panel.get_latest_info()
                worker = self._detect_panel.detect_worker
                if info and worker and worker.latest_detection:
                    frame_path = self.agent.perception.save_frame(worker.latest_detection)
                    self.agent.data.insert_detection(info, frame_path)
                    self._handle_detect_info(info, frame_path)
                    return
            self.append_message("ROSA", res.get("message", "检测失败"), COLOR_RED)
            return

        return self._handle_detect_info(
            res.get("detection", {}),
            res.get("frame_saved", ""),
        )

    def _handle_detect_info(self, info, frame_path):
        model_name = "N/A"
        if self.agent and self.agent.perception and self.agent.perception.model_path:
            model_name = Path(self.agent.perception.model_path).name

        lines = [
            f"检测完成 — 模型: {model_name}",
            f"目标: {info.get('summary', '无')}",
            f"数量: {info.get('count', 0)}",
            f"帧已保存至 QRS/images/",
        ]

        self.append_message("ROSA", "\n".join(lines), COLOR_SYSTEM)

        if self.agent and self.agent.perception.is_loaded:
            latest = self.agent.perception.get_latest_detection()
            if latest and latest.annotated_frame is not None:
                self._show_detect_preview(latest.annotated_frame)

    def _show_detect_preview(self, frame):
        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg).copy()

            pw = self._detect_panel.video_label.width() if self._detect_panel else 280
            ph = self._detect_panel.video_label.height() if self._detect_panel else 200
            if pw > 10 and ph > 10:
                scaled = pixmap.scaled(pw, ph, Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
            else:
                scaled = pixmap.scaled(280, 200, Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
            if self._detect_panel:
                self._detect_panel.video_label.setPixmap(scaled)
        except Exception:
            pass

    def _stream_chat(self, text):
        if self._stream_worker and self._stream_worker.isRunning():
            return

        self._messages.append({"role": "user", "content": text})

        self._stream_buffer = ""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertBlock()
        cursor.insertHtml(f'<b style="color:{COLOR_REPLY};">ROSA: </b>')
        self._stream_anchor = cursor.position()
        self.chat_display.setTextCursor(cursor)

        self.statusBar().showMessage("生成回复中...")
        self._stream_worker = ROSAStreamWorker(self.agent, text)
        self._stream_worker.chunk.connect(self._on_stream_chunk)
        self._stream_worker.finished.connect(self._on_stream_finished)
        self._stream_worker.error.connect(self._on_stream_error)
        self._stream_worker.start()

    def _on_stream_chunk(self, text):
        self._stream_buffer += text
        rendered = md_to_html(self._stream_buffer)
        cursor = self.chat_display.textCursor()
        cursor.setPosition(self._stream_anchor)
        cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertHtml(f'<span style="color:{COLOR_REPLY};">{rendered}</span>')
        self.chat_display.ensureCursorVisible()

    def _on_stream_finished(self, content):
        self._stream_worker = None
        self._messages.append({"role": "assistant", "content": content})
        self.chat_display.append("")
        self.send_btn.setEnabled(True)
        self.statusBar().showMessage("就绪")

    def _on_stream_error(self, msg):
        self._stream_worker = None
        self.chat_display.append(f'<span style="color:red;">[错误] {msg}</span>')
        self.send_btn.setEnabled(True)
        self.statusBar().showMessage("请求出错")

    def _on_process_error(self, msg):
        self._process_worker = None
        self.append_message("ROSA", f"处理错误: {msg}", COLOR_RED)
        self.send_btn.setEnabled(True)
        self.statusBar().showMessage("处理出错")

    def _show_data_records(self):
        if not self.agent:
            return
        records = self.agent.data.get_records(limit=20)
        QMessageBox.information(
            self, "数据记录",
            json.dumps(records, ensure_ascii=False, indent=2)[:2000]
        )

    def _show_config(self):
        if not self.agent:
            return
        QMessageBox.information(
            self, "当前配置",
            json.dumps(self.agent.config.to_dict(), ensure_ascii=False, indent=2)
        )

    def append_message(self, sender, text, color):
        rendered = md_to_html(text)
        self.chat_display.append(
            f'<b style="color:{color};">{sender}:</b><br>'
            f'<span style="color:#1a1a1a;">{rendered}</span>'
        )
        self.chat_display.append("")

    def clear_chat(self):
        self._messages = []
        self._stream_buffer = ""
        self.chat_display.clear()
        self.decision_label.setText("决策: 等待输入...")
        self.statusBar().showMessage("已清屏")

    def closeEvent(self, event):
        if self._process_worker and self._process_worker.isRunning():
            self._process_worker.terminate()
            self._process_worker.wait()
        if self._stream_worker and self._stream_worker.isRunning():
            self._stream_worker.terminate()
            self._stream_worker.wait()
        if self._detect_panel:
            self._detect_panel.shutdown()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    try:
        window = ROSAWindow()
        window.show()
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
