import json
import re
import sys
from pathlib import Path

import cv2
from PyQt6.QtCore import Qt, QEvent, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCursor, QImage, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QTextBrowser, QPushButton, QLabel, QLineEdit, QDialog,
    QDialogButtonBox, QFormLayout, QMessageBox, QComboBox,
    QGroupBox, QSizePolicy, QFrame, QFileDialog,
)
from networkx.algorithms.bipartite.basic import color

SRC_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SRC_DIR))

from rosa import ROSAAgent
from rosa.rosa_decision_midware import ActionType
from rosa.rosa_tts_midware import TTSMiddleware, TTSWorker, TTSLoadWorker
from rosa.rosa_stt_midware import STTMiddleware, STTWorker
from rosa.rosa_model_midware import ModelMiddleware

COLOR_USER = "#16a085"
COLOR_REPLY = "#e65100"
COLOR_SYSTEM = "#1565c0"
COLOR_RED = "#c62828"
COLOR_ON = "#1b5e20"
COLOR_OFF = "#757575"

TTSP_ON = "语音输出: 开"
TTSP_OFF = "语音输出: 关"
STT_ON = "语音输入: 开"
STT_OFF = "语音输入: 关"

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


class ROSADetectPanel(QWidget):
    stop_requested = pyqtSignal()

    def __init__(self, agent, parent=None):
        super().__init__(parent)
        self.agent = agent
        self._last_info = None
        self._last_pixmap = None
        self._stopped = False
        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll_detection)
        self.setMinimumWidth(280)
        self.setMaximumWidth(420)
        self._init_ui()

    def is_running(self):
        return self.agent.perception.is_monitoring

    def get_latest_info(self):
        return self._last_info

    def get_latest_pixmap(self):
        return self._last_pixmap

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

        if self.agent.perception.is_monitoring:
            self.agent.perception.stop_monitoring()

        if not self.agent.perception.is_loaded or self.agent.perception.model_path != model_path:
            self.agent.perception.load_model(model_path)

        self.agent.perception.start_monitoring(device=0)
        self._poll_timer.start(33)
        self.show()

    def attach(self, model_path=""):
        self._stopped = False
        if model_path:
            self.model_label.setText(f"模型: {Path(model_path).name}")
        self._poll_timer.start(33)
        self.show()

    def _poll_detection(self):
        detection = self.agent.perception.get_latest_detection()
        if detection is None:
            return
        info = detection.to_dict()
        self._last_info = info

        if detection.annotated_frame is not None:
            rgb = cv2.cvtColor(detection.annotated_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg).copy()
            self._last_pixmap = pixmap

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

    def _on_stop(self):
        self.agent.perception.stop_monitoring()
        self._poll_timer.stop()
        self.video_label.setText("检测已停止")
        self._emit_stop_once()

    def _emit_stop_once(self):
        if not self._stopped:
            self._stopped = True
            self.stop_requested.emit()

    def shutdown(self):
        if self.agent.perception.is_monitoring:
            self.agent.perception.stop_monitoring()
        self._poll_timer.stop()
        self._emit_stop_once()

class ApiKeyDialog(QDialog):
    def __init__(self, current_key="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置 API Key")
        self.setMinimumWidth(420)
        layout = QFormLayout(self)
        self._input = QLineEdit(current_key or "")
        self._input.setEchoMode(QLineEdit.EchoMode.Password)
        self._input.setPlaceholderText("输入 DeepSeek API Key...")
        self._input.setMinimumWidth(320)
        layout.addRow("API Key:", self._input)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_api_key(self):
        return self._input.text().strip()


class ModelSelectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择 YOLO 模型")
        self.setMinimumWidth(360)
        self._model_path = ""

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("QRS/models/ 中的模型文件:"))

        self._combo = QComboBox()
        QRS_MODELS = Path(__file__).resolve().parent.parent.parent.parent / "QRS" / "models"
        pt_files = sorted(QRS_MODELS.glob("*.pt")) if QRS_MODELS.exists() else []
        if pt_files:
            for pt in pt_files:
                self._combo.addItem(pt.name, str(pt))
        else:
            self._combo.addItem("(未找到 .pt 文件)", "")
        layout.addWidget(self._combo)

        self.path_label = QLabel("")
        self.path_label.setStyleSheet("color: #666; font-size: 9pt;")
        layout.addWidget(self.path_label)

        self._combo.currentIndexChanged.connect(self._on_select)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_ok)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if pt_files:
            self._combo.setCurrentIndex(0)

    def _on_select(self, index):
        path = self._combo.currentData()
        if path and Path(path).exists():
            self._model_path = path
            self.path_label.setText(str(path))
        else:
            self._model_path = ""
            self.path_label.setText("")

    def _on_ok(self):
        if self._combo.currentData():
            self._model_path = self._combo.currentData()
            self.accept()
        else:
            browse = QFileDialog.getOpenFileName(
                self, "选择 YOLO 模型文件", str(Path.home()),
                "模型文件 (*.pt);;所有文件 (*.*)"
            )
            if browse[0]:
                self._model_path = browse[0]
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
        self.models = ModelMiddleware()
        self.tts = TTSMiddleware()
        self.stt = STTMiddleware()
        self._tts_worker = None
        self._tts_load_worker = None
        self._stt_worker = None
        self._init_agent()
        self.init_ui()
        self._check_deps()

    def _init_agent(self):
        try:
            self.agent = ROSAAgent()
        except Exception:
            self.agent = ROSAAgent.__new__(ROSAAgent)
        self._auto_load_model()

    def _auto_load_model(self):
        if not self.agent or not hasattr(self.agent, "perception"):
            return
        QRS_MODELS = Path(__file__).resolve().parent.parent.parent.parent / "QRS" / "models"
        for model_name in ["yolo26s.pt", "yolo26n.pt"]:
            path = QRS_MODELS / model_name
            if path.exists():
                try:
                    self.agent.perception.load_model(str(path))
                    self.agent.config.set("perception", "model_path", value=str(path))
                    return
                except Exception:
                    pass

    def _check_deps(self):
        missing = []
        if not self.models.check_pyaudio():
            missing.append("pyaudio (语音)")
        if not self.models.check_piper():
            missing.append("piper-tts (语音输出)")
        if not self.models.check_vosk():
            missing.append("vosk (语音输入)")
        if missing:
            self.statusBar().showMessage(
                f"提示: 缺少依赖包 — {', '.join(missing)}"
            )

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
            "QTextEdit { background-color: #f5f5f5; border: 1px solid #ccc; "
            "border-radius: 4px; padding: 8px; color: #7b1fa2; }"
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
        self.decision_label.setStyleSheet("color: #1b5e20;")
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

        self.tts_btn = QPushButton(TTSP_ON)
        self.tts_btn.setMinimumHeight(28)
        self.tts_btn.setStyleSheet(
            f"QPushButton {{ background-color: {COLOR_ON}; color: white; border: none; "
            "border-radius: 4px; font-weight: bold; font-size: 10pt; }}"
        )
        self.tts_btn.clicked.connect(self._toggle_tts)
        btn_layout.addWidget(self.tts_btn)

        self.stt_btn = QPushButton(STT_OFF)
        self.stt_btn.setMinimumHeight(28)
        self.stt_btn.setStyleSheet(
            f"QPushButton {{ background-color: {COLOR_OFF}; color: white; border: none; "
            "border-radius: 4px; font-weight: bold; font-size: 10pt; }}"
        )
        self.stt_btn.clicked.connect(self._toggle_stt)
        btn_layout.addWidget(self.stt_btn)

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

    def _toggle_tts(self):
        self.tts.enabled = not self.tts.enabled
        if self.tts.enabled:
            self.tts_btn.setText(TTSP_ON)
            self.tts_btn.setStyleSheet(
                f"QPushButton {{ background-color: {COLOR_ON}; color: white; border: none; "
                "border-radius: 4px; font-weight: bold; font-size: 10pt; }}"
            )
            if not self.tts.is_loaded:
                self.tts_btn.setText("加载中...")
                self.tts_btn.setEnabled(False)
                self._tts_load_worker = TTSLoadWorker(self.tts)
                self._tts_load_worker.loaded.connect(self._on_tts_loaded)
                self._tts_load_worker.error.connect(self._on_tts_load_error)
                self._tts_load_worker.start()
        else:
            self.tts_btn.setText(TTSP_OFF)
            self.tts_btn.setStyleSheet(
                f"QPushButton {{ background-color: {COLOR_OFF}; color: white; border: none; "
                "border-radius: 4px; font-weight: bold; font-size: 10pt; }}"
            )
            self.statusBar().showMessage("TTS 已关闭")

    def _on_tts_loaded(self, model_path):
        self._tts_load_worker = None
        self.tts_btn.setEnabled(True)
        self.tts_btn.setText(TTSP_ON)
        self.tts_btn.setStyleSheet(
            f"QPushButton {{ background-color: {COLOR_ON}; color: white; border: none; "
            "border-radius: 4px; font-weight: bold; font-size: 10pt; }}"
        )
        self.statusBar().showMessage(f"TTS 模型已加载: {Path(model_path).name}" if model_path else "TTS 模型已加载")

    def _on_tts_load_error(self, msg):
        self._tts_load_worker = None
        self.tts.enabled = False
        self.tts_btn.setEnabled(True)
        self.tts_btn.setText(TTSP_OFF)
        self.tts_btn.setStyleSheet(
            f"QPushButton {{ background-color: {COLOR_OFF}; color: white; border: none; "
            "border-radius: 4px; font-weight: bold; font-size: 10pt; }}"
        )
        QMessageBox.warning(self, "语音输出不可用", f"TTS 模型加载失败:\n{msg}")
        self.statusBar().showMessage("TTS 加载失败")

    def _toggle_stt(self):
        if self._stt_worker and self._stt_worker.isRunning():
            self._stt_worker.stop()
            self._stt_worker.wait(3000)
            self._stt_worker = None
            self.stt_btn.setText(STT_OFF)
            self.stt_btn.setStyleSheet(
                f"QPushButton {{ background-color: {COLOR_OFF}; color: white; border: none; "
                "border-radius: 4px; font-weight: bold; font-size: 10pt; }}"
            )
            self.statusBar().showMessage("语音输入已关闭")
            return

        self.stt_btn.setText("加载中...")
        self.stt_btn.setEnabled(False)
        self._stt_worker = STTWorker(self.stt)
        self._stt_worker.text_ready.connect(self._on_stt_text)
        self._stt_worker.partial_ready.connect(lambda t: self.statusBar().showMessage(f"识别中: {t}"))
        self._stt_worker.error.connect(self._on_stt_error)
        self._stt_worker.status_changed.connect(self._on_stt_status)
        self._stt_worker.start()

    def _on_stt_text(self, text):
        current = self.input_field.toPlainText().strip()
        if current:
            self.input_field.setPlainText(f"{current} {text}")
        else:
            self.input_field.setPlainText(text)

    def _on_stt_status(self, running):
        self.stt_btn.setEnabled(True)
        if running:
            self.stt_btn.setText(STT_ON)
            self.stt_btn.setStyleSheet(
                f"QPushButton {{ background-color: {COLOR_ON}; color: white; border: none; "
                "border-radius: 4px; font-weight: bold; font-size: 10pt; }}"
            )
        else:
            self.stt_btn.setText(STT_OFF)
            self.stt_btn.setStyleSheet(
                f"QPushButton {{ background-color: {COLOR_OFF}; color: white; border: none; "
                "border-radius: 4px; font-weight: bold; font-size: 10pt; }}"
            )

    def _on_stt_error(self, msg):
        self._stt_worker = None
        self.stt_btn.setEnabled(True)
        self.stt_btn.setText(STT_OFF)
        self.stt_btn.setStyleSheet(
            f"QPushButton {{ background-color: {COLOR_OFF}; color: white; border: none; "
            "border-radius: 4px; font-weight: bold; font-size: 10pt; }}"
        )
        QMessageBox.warning(self, "语音输入不可用", msg)
        self.statusBar().showMessage(f"语音输入错误: {msg.split(chr(10))[0]}")

    def _speak_reply(self, text):
        if self._tts_worker and self._tts_worker.isRunning():
            self._tts_worker.terminate()
            self._tts_worker.wait()
        self._tts_worker = TTSWorker(self.tts, text)
        self._tts_worker.error.connect(
            lambda e: self.statusBar().showMessage(f"TTS 播放失败: {e[:80]}")
        )
        self._tts_worker.start()

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
                self._speak_reply(reply)
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
                detection = self.agent.perception.get_latest_detection()
                if info and detection:
                    frame_path = self.agent.perception.save_frame(detection)
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
        self._speak_reply(content)

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
        self.chat_display.append(f'<b style="color:{color};">{sender}:</b><br>{rendered}')
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
        if self._tts_worker and self._tts_worker.isRunning():
            self._tts_worker.terminate()
            self._tts_worker.wait()
        if self._tts_load_worker and self._tts_load_worker.isRunning():
            self._tts_load_worker.terminate()
            self._tts_load_worker.wait()
        if self._stt_worker and self._stt_worker.isRunning():
            self._stt_worker.stop()
            self._stt_worker.wait(3000)
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
