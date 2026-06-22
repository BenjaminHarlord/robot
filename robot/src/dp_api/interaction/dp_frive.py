import json
import os
import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QLineEdit, QDialog, QDialogButtonBox,
    QFormLayout, QMessageBox, QComboBox, QDoubleSpinBox, QSpinBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor, QKeyEvent


class ApiWorker(QThread):
    chunk_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, base_url, api_key, model, messages, temperature, max_tokens):
        super().__init__()
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.messages = messages
        self.temperature = temperature
        self.max_tokens = max_tokens

    def run(self):
        try:
            url = f"{self.base_url}/chat/completions"
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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置 API Key")
        self.setMinimumWidth(450)
        layout = QFormLayout(self)

        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        current_key = os.environ.get("DEEPSEEK_API_KEY", "")
        self.key_input.setText(current_key)
        self.key_input.setPlaceholderText("输入你的 DeepSeek API Key")
        layout.addRow("API Key:", self.key_input)

        hint = QLabel(
            '<a href="https://platform.deepseek.com/api_keys" style="color:#4a90d9;">'
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
        self.init_config()
        self.init_ui()

    def init_config(self):
        config_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "key_json", "dp_config.json"
        )
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        servers = self.config.get("servers", [])
        self.base_url = servers[0]["url"] if servers else "https://api.deepseek.com"

        paths = self.config.get("paths", {})
        chat_info = paths.get("/chat/completions", {}).get("post", {})
        schema = (
            chat_info.get("requestBody", {})
            .get("content", {})
            .get("application/json", {})
            .get("schema", {})
        )
        props = schema.get("properties", {})
        self.default_model = props.get("model", {}).get("default", "deepseek-v4-flash")
        self.default_temperature = props.get("temperature", {}).get("default", 1.0)
        self.default_max_tokens = props.get("max_tokens", {}).get("default", 4096)

        self.messages = []

    def init_ui(self):
        self.setWindowTitle("DeepSeek V4 Flash 聊天助手")
        self.setGeometry(120, 80, 880, 680)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(8)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)

        controls_layout.addWidget(QLabel("模型:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["deepseek-v4-flash", "deepseek-v4-pro"])
        self.model_combo.setCurrentText(self.default_model)
        self.model_combo.setToolTip("选择模型：flash 为快速模型，pro 为推理模型")
        controls_layout.addWidget(self.model_combo)

        controls_layout.addSpacing(16)
        controls_layout.addWidget(QLabel("温度:"))
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 2.0)
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

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet(
            "QTextEdit { background-color: #f5f5f5; border: 1px solid #ccc; border-radius: 4px; padding: 8px; }"
        )
        self.chat_display.setFont(QFont("Microsoft YaHei", 10))
        main_layout.addWidget(self.chat_display, stretch=1)

        input_layout = QHBoxLayout()
        input_layout.setSpacing(6)

        self.input_field = QTextEdit()
        self.input_field.setMaximumHeight(100)
        self.input_field.setMinimumHeight(50)
        self.input_field.setPlaceholderText("输入消息，按 Ctrl+Enter 发送...")
        self.input_field.setFont(QFont("Microsoft YaHei", 10))
        self.input_field.setStyleSheet(
            "QTextEdit { border: 1px solid #aaa; border-radius: 4px; padding: 6px; }"
        )
        input_layout.addWidget(self.input_field, stretch=1)

        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(4)

        self.send_btn = QPushButton("发送")
        self.send_btn.setMinimumHeight(28)
        self.send_btn.setStyleSheet(
            "QPushButton { background-color: #4a90d9; color: white; border: none; border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background-color: #357abd; }"
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
        dialog = ApiKeyDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            key = dialog.get_api_key()
            if key:
                os.environ["DEEPSEEK_API_KEY"] = key
                self.statusBar().showMessage("API Key 已设置")
            else:
                self.statusBar().showMessage("API Key 已清除")

    def get_api_key(self):
        return os.environ.get("DEEPSEEK_API_KEY", "")

    def send_message(self):
        text = self.input_field.toPlainText().strip()
        if not text:
            return

        api_key = self.get_api_key()
        if not api_key:
            QMessageBox.warning(self, "提示", "请先在 设置 > 设置 API Key 中配置 API Key")
            return

        if self.worker and self.worker.isRunning():
            QMessageBox.information(self, "提示", "请等待上一个回复完成")
            return

        self.messages.append({"role": "user", "content": text})
        self.append_message("你", text, "#2c3e50")
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

        model = self.model_combo.currentText()
        temperature = self.temperature_spin.value()
        max_tokens = self.max_tokens_spin.value()

        self.worker = ApiWorker(
            self.base_url, api_key, model,
            self.messages.copy(), temperature, max_tokens
        )
        self.worker.chunk_signal.connect(self.on_chunk)
        self.worker.finished_signal.connect(self.on_finished)
        self.worker.error_signal.connect(self.on_error)
        self.worker.start()

    def on_chunk(self, text):
        self.stream_buffer += text
        cursor = self.chat_display.textCursor()
        cursor.setPosition(self.stream_anchor)
        cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(text)
        self.chat_display.ensureCursorVisible()

    def on_finished(self, data):
        content = data.get("content", "")
        if content:
            self.messages.append({"role": "assistant", "content": content})
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

    def append_message(self, sender, text, color):
        escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.chat_display.append(
            f'<b style="color:{color};">{sender}:</b><br>{escaped}'
        )
        self.chat_display.append("")

    def clear_chat(self):
        self.messages = []
        self.stream_buffer = ""
        self.chat_display.clear()
        self.statusBar().showMessage("已清屏")

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
