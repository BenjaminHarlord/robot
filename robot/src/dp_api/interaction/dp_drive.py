import csv
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import requests
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl
from PyQt6.QtGui import QFont, QTextCursor, QDesktopServices
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QTextBrowser, QPushButton, QLabel, QLineEdit, QDialog, QDialogButtonBox,
    QFormLayout, QMessageBox, QComboBox, QDoubleSpinBox, QSpinBox
)

SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parents[3]
MIDDLEWARE_DIR = WORKSPACE_ROOT / "robot" / "tool_chain" / "Middleware"
if str(MIDDLEWARE_DIR) not in sys.path:
    sys.path.insert(0, str(MIDDLEWARE_DIR))

from dp_chat import ChatImageMiddleware, ImageResearchConfig, extract_image_urls

USER_CONFIG_PATH = WORKSPACE_ROOT / "robot" / "dataclume" / "user" / "user.json"
CSV_RECORD_DIR = Path("/home/andre/dev_root/robot/QRP/dp_record")
MAX_RECORDS_PER_FILE = 100000
CSV_FIELDS = ["u_id", "u_na", "u_position", "u_message", "model_name", "u_tkTime", "u_ask"]

_MD_IMG_RE = re.compile(r'!\[([^\]]*)\]\(([^)\s]+)\)')
_MD_LINK_RE = re.compile(r'(?<!\!)\[([^\]]+)\]\(([^)\s]+)\)')
_MD_BOLD_RE = re.compile(r'\*\*(.+?)\*\*')
_MD_ITALIC_RE = re.compile(r'\*(.+?)\*')
_MD_CODE_INLINE_RE = re.compile(r'`([^`]+)`')
_MD_CODE_BLOCK_RE = re.compile(r'```(\w*)\n?(.*?)```', re.DOTALL)
_RAW_IMG_URL_RE = re.compile(r'(https?://[^\s<>"\']+\.(?:png|jpe?g|gif|webp|bmp|svg)(?:\?[^\s<>"\']*)?)', re.IGNORECASE)


def md_to_html(text):
    buf = text

    blocks = []
    last = 0
    for m in _MD_CODE_BLOCK_RE.finditer(buf):
        blocks.append(("text", buf[last:m.start()]))
        lang = m.group(1) or ""
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
            part = _MD_LINK_RE.sub(r'<a href="\2" style="color:#2e7d32;">\1</a>', part)
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

    html = "".join(result_parts)
    return html


class UserConfig:
    def __init__(self, config_path):
        self.config_path = Path(config_path)
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = {}

    @property
    def user_id(self):
        return self.data.get("id", "")

    @property
    def user_name(self):
        return self.data.get("name", "")

    @property
    def user_position(self):
        return self.data.get("position", "")

    def get_api_key(self):
        key = self.data.get("dp_apikey", "")
        return key.strip() if key and key.strip() != "sk-" else ""

    def set_api_key(self, key):
        self.data["dp_apikey"] = key
        self._save()

    def _save(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)


class OpenApiConfig:
    def __init__(self, config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            self.raw = json.load(f)
        self._parse()

    def _parse(self):
        self.title = self.raw.get("info", {}).get("title", "")
        servers = self.raw.get("servers", [])
        if not servers:
            raise ValueError("OpenAPI 配置缺少 servers")
        self.base_url = servers[0].get("url", "").rstrip("/")
        if not self.base_url:
            raise ValueError("servers[0].url 为空")
        self.paths = self.raw.get("paths", {})
        if not self.paths:
            raise ValueError("OpenAPI 配置缺少 paths")
        self.auth_scheme = self._parse_auth()
        self.endpoints = {}
        for path, methods in self.paths.items():
            for method, spec in methods.items():
                if not isinstance(spec, dict):
                    continue
                key = (method.upper(), path)
                self.endpoints[key] = self._parse_endpoint(spec)

    def _parse_auth(self):
        security = self.raw.get("security", [])
        if not security:
            return None
        schemes = self.raw.get("components", {}).get("securitySchemes", {})
        for sec_req in security:
            for name in sec_req:
                if name in schemes:
                    scheme = schemes[name]
                    return {
                        "name": name,
                        "type": scheme.get("type", ""),
                        "scheme": scheme.get("scheme", ""),
                        "bearerFormat": scheme.get("bearerFormat", ""),
                    }
        return None

    def _parse_endpoint(self, spec):
        operation_id = spec.get("operationId", "")
        description = spec.get("description", "")
        request_schema = {}
        content = spec.get("requestBody", {}).get("content", {})
        json_body = content.get("application/json", {})
        if json_body:
            request_schema = json_body.get("schema", {})
        return {
            "operationId": operation_id,
            "description": description,
            "requestSchema": request_schema,
        }

    def get_endpoint(self, method, path):
        return self.endpoints.get((method.upper(), path))

    def get_request_properties(self, method, path):
        ep = self.get_endpoint(method, path)
        if not ep:
            return {}
        return ep.get("requestSchema", {}).get("properties", {})

    def get_required_fields(self, method, path):
        ep = self.get_endpoint(method, path)
        if not ep:
            return []
        return ep.get("requestSchema", {}).get("required", [])

    def get_prop_default(self, method, path, prop_name, fallback=None):
        props = self.get_request_properties(method, path)
        return props.get(prop_name, {}).get("default", fallback)

    def get_prop_enum(self, method, path, prop_name):
        props = self.get_request_properties(method, path)
        return props.get(prop_name, {}).get("enum", [])

    def get_prop_min(self, method, path, prop_name):
        props = self.get_request_properties(method, path)
        return props.get(prop_name, {}).get("minimum")

    def get_prop_max(self, method, path, prop_name):
        props = self.get_request_properties(method, path)
        return props.get(prop_name, {}).get("maximum")


class ApiWorker(QThread):
    chunk_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, base_url, api_key, model, messages, temperature, max_tokens, endpoint_path):
        super().__init__()
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.messages = messages
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.endpoint_path = endpoint_path

    def run(self):
        try:
            url = f"{self.base_url}{self.endpoint_path}"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            body = {
                "model": self.model,
                "messages": self.messages,
                "stream": True,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "thinking": {"type": "disabled"},
            }
            response = requests.post(url, headers=headers, json=body, stream=True, timeout=120)
            if response.status_code != 200:
                self.error_signal.emit(f"HTTP {response.status_code}: {response.text[:500]}")
                return
            full_content = ""
            for line in response.iter_lines(decode_unicode=True):
                if line and line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        choices = data.get("choices", [])
                        if choices:
                            delta = choices[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                full_content += content
                                self.chunk_signal.emit(content)
                    except json.JSONDecodeError:
                        pass
            self.finished_signal.emit({"content": full_content})
        except requests.exceptions.Timeout:
            self.error_signal.emit("请求超时，请检查网络")
        except requests.exceptions.ConnectionError:
            self.error_signal.emit("连接失败，请检查网络设置")
        except Exception as e:
            self.error_signal.emit(str(e))


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
            '<a href="https://platform.deepseek.com/api_keys" style="color:#2e7d32;">'
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


class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.stream_buffer = ""
        self.stream_anchor = None
        self.messages = []
        self.current_ask = ""
        self.image_middleware = ChatImageMiddleware()
        self.image_middleware.image_fetched.connect(self._on_image_ready)
        self.init_config()
        self.init_ui()

    def init_config(self):
        config_path = SCRIPT_DIR / ".." / "key_json" / "dp_config.json"
        self.api_config = OpenApiConfig(str(config_path))
        self.user_config = UserConfig(str(USER_CONFIG_PATH))
        self.CHAT_METHOD = "POST"
        self.CHAT_PATH = "/chat/completions"
        self.base_url = self.api_config.base_url
        self.default_model = self.api_config.get_prop_default(
            self.CHAT_METHOD, self.CHAT_PATH, "model", "deepseek-v4-flash"
        )
        self.default_temperature = self.api_config.get_prop_default(
            self.CHAT_METHOD, self.CHAT_PATH, "temperature", 1.0
        )
        self.default_max_tokens = self.api_config.get_prop_default(
            self.CHAT_METHOD, self.CHAT_PATH, "max_tokens", 4096
        )
        self.available_models = self.api_config.get_prop_enum(
            self.CHAT_METHOD, self.CHAT_PATH, "model"
        )
        self.temp_min = self.api_config.get_prop_min(self.CHAT_METHOD, self.CHAT_PATH, "temperature") or 0.0
        self.temp_max = self.api_config.get_prop_max(self.CHAT_METHOD, self.CHAT_PATH, "temperature") or 2.0

    def init_ui(self):
        self.setWindowTitle(f"{self.api_config.title} 聊天助手")
        self.setGeometry(120, 80, 960, 720)
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(8)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.addWidget(QLabel("模型:"))
        self.model_combo = QComboBox()
        models = self.available_models if self.available_models else ["deepseek-v4-flash", "deepseek-v4-pro"]
        self.model_combo.addItems(models)
        idx = self.model_combo.findText(self.default_model)
        if idx >= 0:
            self.model_combo.setCurrentIndex(idx)
        self.model_combo.setToolTip("选择模型：flash 为快速模型，pro 为推理模型")
        controls_layout.addWidget(self.model_combo)
        controls_layout.addSpacing(16)
        controls_layout.addWidget(QLabel("温度:"))
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(self.temp_min, self.temp_max)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setValue(self.default_temperature)
        self.temperature_spin.setToolTip("采样温度，越高越随机")
        controls_layout.addWidget(self.temperature_spin)
        controls_layout.addSpacing(16)
        controls_layout.addWidget(QLabel("最大 Token:"))
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(1, 32768)
        self.max_tokens_spin.setSingleStep(256)
        self.max_tokens_spin.setValue(self.default_max_tokens)
        self.max_tokens_spin.setToolTip("生成回复的最大 token 数")
        controls_layout.addWidget(self.max_tokens_spin)
        controls_layout.addStretch()
        main_layout.addLayout(controls_layout)

        self.chat_display = QTextBrowser()
        self.chat_display.setReadOnly(True)
        self.chat_display.setOpenExternalLinks(True)
        self.chat_display.setStyleSheet(
            "QTextEdit { background-color: #f5f5f5; border: 1px solid #ccc; "
            "border-radius: 4px; padding: 8px; }"
        )
        self.chat_display.setFont(QFont("Microsoft YaHei", 12))
        self.chat_display.anchorClicked.connect(self._on_link_clicked)
        main_layout.addWidget(self.chat_display, stretch=1)

        input_layout = QHBoxLayout()
        input_layout.setSpacing(6)
        self.input_field = QTextEdit()
        self.input_field.setMaximumHeight(100)
        self.input_field.setMinimumHeight(50)
        self.input_field.setPlaceholderText("输入消息，按 Ctrl+Enter 发送...")
        self.input_field.setFont(QFont("Microsoft YaHei", 12))
        self.input_field.setStyleSheet(
            "QTextEdit { border: 1px solid #aaa; border-radius: 4px; padding: 6px; }"
        )
        input_layout.addWidget(self.input_field, stretch=1)
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(4)
        self.send_btn = QPushButton("发送")
        self.send_btn.setMinimumHeight(28)
        self.send_btn.setStyleSheet(
            "QPushButton { background-color: #2e7d32; color: white; border: none; "
            "border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background-color: #1b5e20; }"
            "QPushButton:disabled { background-color: #aaa; }"
        )
        self.send_btn.clicked.connect(self.send_message)
        btn_layout.addWidget(self.send_btn)
        self.clear_btn = QPushButton("清屏")
        self.clear_btn.setMinimumHeight(28)
        self.clear_btn.clicked.connect(self.clear_chat)
        btn_layout.addWidget(self.clear_btn)
        input_layout.addLayout(btn_layout)
        main_layout.addLayout(input_layout)

        self.statusBar().showMessage("就绪 | 请先设置 API Key")
        menubar = self.menuBar()
        settings_menu = menubar.addMenu("设置")
        apikey_action = settings_menu.addAction("设置 API Key")
        apikey_action.triggered.connect(self.show_api_key_dialog)

    def keyPressEvent(self, event):
        if (
            event.key() == Qt.Key.Key_Return
            and event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            if self.input_field.hasFocus():
                self.send_message()
                return
        super().keyPressEvent(event)

    def show_api_key_dialog(self):
        current_key = self.user_config.get_api_key()
        dialog = ApiKeyDialog(current_key, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            key = dialog.get_api_key()
            if key:
                self.user_config.set_api_key(key)
                self.statusBar().showMessage("API Key 已保存")
            else:
                self.user_config.set_api_key("")
                self.statusBar().showMessage("API Key 已清除")

    def get_api_key(self):
        return self.user_config.get_api_key()

    def send_message(self):
        text = self.input_field.toPlainText().strip()
        if not text:
            return
        api_key = self.get_api_key()
        if not api_key:
            self.show_api_key_dialog()
            api_key = self.get_api_key()
            if not api_key:
                return
        if self.worker and self.worker.isRunning():
            QMessageBox.information(self, "提示", "请等待上一个回复完成")
            return

        user_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.messages.append({"role": "user", "content": text})
        self.current_ask = text
        self.append_message("你", text, "#333333")
        self._save_record(text, user_time)
        self.input_field.clear()

        self.send_btn.setEnabled(False)
        self.statusBar().showMessage("正在等待回复...")

        self.stream_buffer = ""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertBlock()
        cursor.insertHtml('<b style="color:#2980b9;">DeepSeek: </b>')
        self.stream_anchor = cursor.position()
        self.chat_display.setTextCursor(cursor)

        self.image_middleware.reset()

        model = self.model_combo.currentText()
        temperature = self.temperature_spin.value()
        max_tokens = self.max_tokens_spin.value()
        self.worker = ApiWorker(
            self.base_url, api_key, model,
            self.messages.copy(), temperature, max_tokens,
            self.CHAT_PATH
        )
        self.worker.chunk_signal.connect(self.on_chunk)
        self.worker.finished_signal.connect(self.on_finished)
        self.worker.error_signal.connect(self.on_error)
        self.worker.start()

    def on_chunk(self, text):
        self.stream_buffer += text
        rendered = md_to_html(self.stream_buffer)
        cursor = self.chat_display.textCursor()
        cursor.setPosition(self.stream_anchor)
        cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertHtml(f'<span style="color:#1a5276;">{rendered}</span>')
        self.chat_display.ensureCursorVisible()
        self.image_middleware.process_chunk(text)

    def on_finished(self, data):
        content = data.get("content", "")
        if content:
            self.messages.append({"role": "assistant", "content": content})
            resp_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._save_record(content, resp_time)
        self.chat_display.append("")
        self.send_btn.setEnabled(True)
        self.statusBar().showMessage("就绪")
        self.worker = None

    def on_error(self, error_msg):
        self.chat_display.append(
            f'<span style="color:red;font-weight:bold;">[错误] {error_msg}</span>'
        )
        self.chat_display.append("")
        if self.stream_buffer:
            self.messages.append({"role": "assistant", "content": self.stream_buffer})
        self.send_btn.setEnabled(True)
        self.statusBar().showMessage("请求出错")
        self.worker = None

    def _on_image_ready(self, url, pixmap, caption):
        pass

    def _on_link_clicked(self, url):
        QDesktopServices.openUrl(QUrl(url.toString()))

    def append_message(self, sender, text, color):
        rendered = md_to_html(text)
        self.chat_display.append(
            f'<b style="color:{color};">{sender}:</b><br>{rendered}'
        )
        self.chat_display.append("")

    def clear_chat(self):
        self.messages = []
        self.stream_buffer = ""
        self.current_ask = ""
        self.chat_display.clear()
        self.image_middleware.reset()
        self.statusBar().showMessage("已清屏")

    def _get_csv_path(self):
        today = datetime.now().strftime("%y%m%d")
        base = CSV_RECORD_DIR / f"{today}.csv"
        if base.exists():
            with open(base, "r", encoding="utf-8") as f:
                line_count = sum(1 for _ in f)
            if line_count >= MAX_RECORDS_PER_FILE:
                idx = 1
                while True:
                    alt = CSV_RECORD_DIR / f"{today}_{idx}.csv"
                    if not alt.exists():
                        return alt
                    with open(alt, "r", encoding="utf-8") as f2:
                        if sum(1 for _ in f2) < MAX_RECORDS_PER_FILE:
                            return alt
                    idx += 1
        return base

    def _save_record(self, message, tk_time):
        CSV_RECORD_DIR.mkdir(parents=True, exist_ok=True)
        csv_path = self._get_csv_path()
        file_exists = csv_path.exists()
        model = self.model_combo.currentText()
        row = {
            "u_id": self.user_config.user_id,
            "u_na": self.user_config.user_name,
            "u_position": self.user_config.user_position,
            "u_message": message,
            "model_name": model,
            "u_tkTime": tk_time,
            "u_ask": self.current_ask,
        }
        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        self.image_middleware.shutdown()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    try:
        window = ChatWindow()
        window.show()
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
