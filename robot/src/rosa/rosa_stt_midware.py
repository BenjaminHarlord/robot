import threading
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

QRS_ROOT = Path(__file__).resolve().parent.parent.parent.parent / "QRS"
DEFAULT_VOSK_DIR = QRS_ROOT / "vosk_models"


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
        if model_path:
            self._model_path = str(Path(model_path))
        if not self._model_path:
            found = self._find_model()
            if found:
                self._model_path = str(found)
            else:
                raise FileNotFoundError(
                    "未找到Vosk语音模型，请放入 QRS/vosk_models/ 或指定路径"
                )
        import vosk
        self._model = vosk.Model(self._model_path)
        return self

    def _find_model(self):
        if not self._vosk_dir.exists():
            return None
        for entry in self._vosk_dir.iterdir():
            if entry.is_dir():
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
        import vosk
        self._recognizer = vosk.KaldiRecognizer(self._model, sample_rate)
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
        import pyaudio
        try:
            if not self.stt.is_loaded:
                self.stt.load_model()
            self.stt.create_recognizer()
            self.stt.reset_recognizer()

            pa = pyaudio.PyAudio()
            stream = pa.open(
                format=pyaudio.paInt16, channels=1, rate=16000,
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
