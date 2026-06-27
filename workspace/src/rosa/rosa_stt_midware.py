import threading
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

QRS_ROOT = Path(__file__).parent.parent.parent.parent / "QRS"
DEFAULT_VOSK_DIR = QRS_ROOT / "vosk_models"

try:
    import pyaudio as _stt_pyaudio
    HAS_STT_PYAUDIO = True
except ImportError:
    _stt_pyaudio = None
    HAS_STT_PYAUDIO = False

try:
    from vosk import Model as VoskModel, KaldiRecognizer
    HAS_STT_VOSK = True
except ImportError:
    VoskModel = None
    KaldiRecognizer = None
    HAS_STT_VOSK = False


class STTMiddleware:
    def __init__(self, model_path=None):
        self._model_path = model_path
        self._model = None
        self._recognizer = None
        self._enabled = False
        self._running = False
        self._lock = threading.Lock()
        self._vosk_dir = DEFAULT_VOSK_DIR
        self._vosk_dir.mkdir(parents=True, exist_ok=True)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value

    @property
    def is_running(self):
        return self._running

    @property
    def is_loaded(self):
        return self._model is not None

    @property
    def model_path(self):
        return self._model_path

    def load_model(self, model_path=None):
        if not HAS_STT_VOSK:
            raise ImportError(
                "缺少 vosk 包，请安装: pip install vosk"
            )
        if model_path:
            self._model_path = str(Path(model_path))
        if not self._model_path:
            found = self._find_model()
            if found:
                self._model_path = str(found)
            else:
                self._download_model()
        self._model = VoskModel(self._model_path)
        return self

    def _download_model(self):
        from .rosa_model_midware import ModelMiddleware
        mm = ModelMiddleware()
        downloaded = mm.ensure_stt_model()
        found = self._find_model()
        if found:
            self._model_path = str(found)
        else:
            raise FileNotFoundError(
                "未找到Vosk语音模型且自动下载失败，请手动放入 QRS/vosk_models/"
            )

    def _find_model(self):
        if not self._vosk_dir.exists():
            return None
        for model_name in ("vosk-model-cn-0.22", "vosk-model-small-cn-0.22"):
            model_dir = self._vosk_dir / model_name
            if not model_dir.is_dir():
                continue
            am_path = model_dir / "am" / "final.mdl"
            conf_path = model_dir / "conf" / "model.conf"
            if am_path.exists() and conf_path.exists():
                return model_dir
            graph_dir = model_dir / "graph"
            if graph_dir.exists():
                return model_dir
        for entry in self._vosk_dir.iterdir():
            if not entry.is_dir():
                continue
            am_path = entry / "am" / "final.mdl"
            conf_path = entry / "conf" / "model.conf"
            if am_path.exists() and conf_path.exists():
                return entry
            graph_dir = entry / "graph"
            if graph_dir.exists():
                return entry
        return None

    def create_recognizer(self, sample_rate=16000):
        if not self._model:
            self.load_model()
        self._recognizer = KaldiRecognizer(self._model, sample_rate)
        self._recognizer.SetWords(True)
        return self._recognizer

    def recognize_once(self, audio_data):
        if not self._recognizer:
            self.create_recognizer()
        if self._recognizer.AcceptWaveform(audio_data):
            import json
            result = json.loads(self._recognizer.Result())
            return result.get("text", "")
        else:
            import json
            partial = json.loads(self._recognizer.PartialResult())
            return partial.get("partial", "")

    def reset_recognizer(self):
        if self._recognizer:
            self._recognizer.Reset()

    def __repr__(self):
        return (
            f"<STTMiddleware loaded={self.is_loaded} "
            f"enabled={self._enabled} "
            f"model={Path(self._model_path).name if self._model_path else 'None'}>"
        )


class STTWorker(QThread):
    text_ready = pyqtSignal(str)
    partial_ready = pyqtSignal(str)
    error = pyqtSignal(str)
    status_changed = pyqtSignal(bool)

    def __init__(self, stt_middleware):
        super().__init__()
        self.stt = stt_middleware
        self._running = True

    def run(self):
        if not HAS_STT_PYAUDIO:
            self.error.emit("缺少 pyaudio 语音库，语音输入不可用：pip install pyaudio")
            self.status_changed.emit(False)
            return
        if not HAS_STT_VOSK:
            self.error.emit("缺少 vosk 包，语音输入不可用：pip install vosk")
            self.status_changed.emit(False)
            return
        try:
            if not self.stt.is_loaded:
                self.stt.load_model()
            self.stt.create_recognizer()
            self.stt.reset_recognizer()

            pa = _stt_pyaudio.PyAudio()
            stream = pa.open(
                format=_stt_pyaudio.paInt16, channels=1, rate=16000,
                input=True, frames_per_buffer=4000,
            )
            stream.start_stream()
            self.status_changed.emit(True)

            while self._running:
                data = stream.read(4000, exception_on_overflow=False)
                if self.stt._recognizer.AcceptWaveform(data):
                    import json
                    result = json.loads(self.stt._recognizer.Result())
                    text = result.get("text", "").strip()
                    if text:
                        self.text_ready.emit(text)
                        self.stt.reset_recognizer()
                else:
                    import json
                    partial = json.loads(self.stt._recognizer.PartialResult())
                    p = partial.get("partial", "").strip()
                    if p:
                        self.partial_ready.emit(p)
                self.msleep(10)

            stream.stop_stream()
            stream.close()
            pa.terminate()
            self.status_changed.emit(False)
        except Exception as e:
            self.error.emit(str(e))
            self.status_changed.emit(False)

    def stop(self):
        self._running = False
