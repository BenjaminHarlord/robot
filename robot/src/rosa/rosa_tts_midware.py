from pathlib import Path
import threading

from PyQt6.QtCore import QThread, pyqtSignal

try:
    import wave
    HAS_WAVE = True
except ImportError:
    HAS_WAVE = False

QRS_ROOT = Path(__file__).resolve().parent.parent.parent.parent / "QRS"
DEFAULT_PIPER_DIR = QRS_ROOT / "piper"


class TTSMiddleware:
    def __init__(self, model_path=None):
        self._model_path = model_path
        self._voice = None
        self._enabled = True
        self._lock = threading.Lock()
        self._piper_dir = DEFAULT_PIPER_DIR
        self._piper_dir.mkdir(parents=True, exist_ok=True)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value

    @property
    def is_loaded(self):
        return self._voice is not None

    @property
    def model_path(self):
        return self._model_path

    def load_model(self, model_path=None):
        if model_path:
            self._model_path = str(Path(model_path))
        if not self._model_path:
            found = self._find_model()
            if found:
                self._model_path = str(found)
            else:
                raise FileNotFoundError(
                    "未找到Piper语音模型(.onnx)，请放入 QRS/piper/ 或指定路径"
                )
        import piper
        self._voice = piper.PiperVoice.load(self._model_path)
        return self

    def _find_model(self):
        if not self._piper_dir.exists():
            return None
        for onnx_file in self._piper_dir.glob("*.onnx"):
            json_file = onnx_file.with_suffix(".onnx.json")
            if json_file.exists():
                return onnx_file
        return None

    def speak(self, text):
        if not self._enabled or not self._voice or not text.strip():
            return False
        with self._lock:
            try:
                import io
                buf = io.BytesIO()
                wav_file = wave.open(buf, "wb")
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(22050)
                self._voice.synthesize(text, wav_file)
                wav_file.close()

                import pyaudio
                import numpy as np
                buf.seek(0)
                with wave.open(buf, "rb") as wf:
                    pa = pyaudio.PyAudio()
                    stream = pa.open(
                        format=pa.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True,
                    )
                    data = wf.readframes(4096)
                    while data:
                        stream.write(data)
                        data = wf.readframes(4096)
                    stream.stop_stream()
                    stream.close()
                    pa.terminate()
                return True
            except Exception:
                return False

    def speak_text_sync(self, text):
        return self.speak(text)

    def __repr__(self):
        return (
            f"<TTSMiddleware loaded={self.is_loaded} "
            f"enabled={self._enabled} model={Path(self._model_path).name if self._model_path else 'None'}>"
        )


class TTSWorker(QThread):
    finished = pyqtSignal()

    def __init__(self, tts_middleware, text):
        super().__init__()
        self.tts = tts_middleware
        self.text = text

    def run(self):
        if self.tts.enabled and self.tts.is_loaded:
            self.tts.speak(self.text)
        self.finished.emit()
