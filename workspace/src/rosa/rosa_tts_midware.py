from pathlib import Path
import threading

from PyQt6.QtCore import QThread, pyqtSignal

QRS_ROOT = Path(__file__).resolve().parent.parent.parent.parent / "QRS"
DEFAULT_PIPER_DIR = QRS_ROOT / "piper"

try:
    import wave
    HAS_WAVE = True
except ImportError:
    HAS_WAVE = False

try:
    import pyaudio as _tts_pyaudio
    HAS_TTS_PYAUDIO = True
except ImportError:
    _tts_pyaudio = None
    HAS_TTS_PYAUDIO = False

try:
    import numpy as _tts_numpy
    HAS_TTS_NUMPY = True
except ImportError:
    _tts_numpy = None
    HAS_TTS_NUMPY = False

try:
    import piper as _tts_piper
    HAS_TTS_PIPER = True
except ImportError:
    _tts_piper = None
    HAS_TTS_PIPER = False


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
        if not HAS_TTS_PIPER:
            raise ImportError(
                "缺少 piper-tts 包，请安装: pip install piper-tts"
            )
        if model_path:
            self._model_path = str(Path(model_path))
        if not self._model_path:
            found = self._find_model()
            if found:
                self._model_path = str(found)
            else:
                self._download_model()
        self._voice = _tts_piper.PiperVoice.load(self._model_path)
        return self

    def _download_model(self):
        from .rosa_model_midware import ModelMiddleware
        mm = ModelMiddleware()
        mm.ensure_tts_model()
        found = self._find_model()
        if found:
            self._model_path = str(found)
        else:
            raise FileNotFoundError(
                "未找到Piper语音模型(.onnx)且自动下载失败，请手动放入 QRS/piper/"
            )

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
            return False, "未启用或无模型"
        if not HAS_WAVE:
            return False, "缺少 wave 模块"
        if not HAS_TTS_PYAUDIO:
            return False, "缺少 pyaudio 模块"
        if not HAS_TTS_NUMPY:
            return False, "缺少 numpy 模块"
        with self._lock:
            try:
                import io
                buf = io.BytesIO()
                wav_file = wave.open(buf, "wb")
                self._voice.synthesize_wav(text, wav_file)
                wav_file.close()

                buf.seek(0)
                with wave.open(buf, "rb") as wf:
                    pa = _tts_pyaudio.PyAudio()
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
                return True, ""
            except Exception as e:
                return False, str(e)

    def speak_text_sync(self, text):
        return self.speak(text)

    def __repr__(self):
        return (
            f"<TTSMiddleware loaded={self.is_loaded} "
            f"enabled={self._enabled} model={Path(self._model_path).name if self._model_path else 'None'}>"
        )


class TTSWorker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, tts_middleware, text):
        super().__init__()
        self.tts = tts_middleware
        self.text = text

    def run(self):
        if self.tts.enabled and self.tts.is_loaded:
            ok, err = self.tts.speak(self.text)
            if not ok:
                self.error.emit(err)
        self.finished.emit()


class TTSLoadWorker(QThread):
    loaded = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, tts_middleware):
        super().__init__()
        self.tts = tts_middleware

    def run(self):
        try:
            if not self.tts.is_loaded:
                self.tts.load_model()
            self.loaded.emit(self.tts._model_path or "")
        except Exception as e:
            self.error.emit(str(e))
