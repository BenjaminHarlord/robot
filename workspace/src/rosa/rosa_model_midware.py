from pathlib import Path
import zipfile
import time

import requests

QRS_ROOT = Path(__file__).parent.parent.parent.parent / "QRS"
PIPER_DIR = QRS_ROOT / "piper"
VOSK_DIR = QRS_ROOT / "vosk_models"

try:
    import pyaudio
    HAS_PYAUDIO = True
except ImportError:
    pyaudio = None
    HAS_PYAUDIO = False

try:
    import numpy
    HAS_NUMPY = True
except ImportError:
    numpy = None
    HAS_NUMPY = False

try:
    import piper as _piper_mod
    HAS_PIPER = True
except ImportError:
    _piper_mod = None
    HAS_PIPER = False

try:
    from vosk import Model as _VoskModel
    HAS_VOSK = True
except ImportError:
    _VoskModel = None
    HAS_VOSK = False

_VOSK_NATIVE = HAS_VOSK and _VoskModel is not None

PIPER_VOICES = {
    "zh_CN-huayan-medium": {
        "onnx": "zh_CN-huayan-medium.onnx",
        "json": "zh_CN-huayan-medium.onnx.json",
        "url_base": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/zh/zh_CN/huayan/medium/",
    },
}

VOSK_MODELS = {
    "vosk-model-cn-0.22": {
        "name": "vosk-model-cn-0.22",
        "url": "https://alphacephei.com/vosk/models/vosk-model-cn-0.22.zip",
        "size": "1.3G",
        "desc": "中文大模型 — 高精度，推荐桌面端使用",
    },
    "vosk-model-small-cn-0.22": {
        "name": "vosk-model-small-cn-0.22",
        "url": "https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip",
        "size": "42M",
        "desc": "中文小模型 — 轻量，适合移动/RPi",
    },
}

VOSK_DEFAULT_MODEL = "vosk-model-cn-0.22"
VOSK_FALLBACK_MODEL = "vosk-model-small-cn-0.22"

_DOWNLOAD_RETRIES = 5
_DOWNLOAD_TIMEOUT = (15, 300)
_CHUNK_SIZE = 131072

_session = None


def _get_session():
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update({"User-Agent": "ROSA-Agent/1.0"})
    return _session


def _download_file(url, dst_path, progress_callback=None, label=""):
    dst_path = Path(dst_path)
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    last_error = None
    for attempt in range(1, _DOWNLOAD_RETRIES + 1):
        try:
            session = _get_session()
            headers = {}
            resume_pos = 0
            if dst_path.exists():
                resume_pos = dst_path.stat().st_size
                if resume_pos > 0:
                    headers["Range"] = f"bytes={resume_pos}-"
                    mode = "ab"
                    if progress_callback:
                        progress_callback(f"{label} 续传中 ({attempt}/{_DOWNLOAD_RETRIES}) ...")
                else:
                    mode = "wb"
            else:
                mode = "wb"
                if progress_callback:
                    progress_callback(f"{label} 下载中 ({attempt}/{_DOWNLOAD_RETRIES}) ...")

            resp = session.get(url, stream=True, timeout=_DOWNLOAD_TIMEOUT, headers=headers)
            resp.raise_for_status()

            total = int(resp.headers.get("content-length", 0))
            if resp.status_code == 206:
                total += resume_pos
            elif resume_pos > 0:
                if progress_callback:
                    progress_callback(f"{label} 服务器不支持续传，重新下载 ...")
                mode = "wb"
                resume_pos = 0
            downloaded = resume_pos

            with open(dst_path, mode) as f:
                for chunk in resp.iter_content(chunk_size=_CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
            return dst_path
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError,
                requests.exceptions.ChunkedEncodingError) as e:
            last_error = e
            if progress_callback:
                progress_callback(f"{label} 故障 (尝试 {attempt}/{_DOWNLOAD_RETRIES})")
            if attempt < _DOWNLOAD_RETRIES:
                time.sleep(3)
        except Exception as e:
            last_error = e
            break

    raise RuntimeError(
        f"下载失败 {label} (重试 {_DOWNLOAD_RETRIES} 次): {last_error}"
    )


class ModelMiddleware:
    def __init__(self):
        PIPER_DIR.mkdir(parents=True, exist_ok=True)
        VOSK_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def check_pyaudio():
        return HAS_PYAUDIO

    @staticmethod
    def check_numpy():
        return HAS_NUMPY

    @staticmethod
    def check_piper():
        return HAS_PIPER

    @staticmethod
    def check_vosk():
        return HAS_VOSK and _VOSK_NATIVE

    def check_tts_ready(self):
        return HAS_PYAUDIO and HAS_NUMPY and HAS_PIPER

    def check_stt_ready(self):
        return HAS_PYAUDIO and HAS_VOSK and _VOSK_NATIVE

    def has_piper_model(self):
        return bool(list(PIPER_DIR.glob("*.onnx")))

    def has_vosk_model(self):
        if not VOSK_DIR.exists():
            return False
        for entry in VOSK_DIR.iterdir():
            if not entry.is_dir():
                continue
            if (entry / "am" / "final.mdl").exists() and (entry / "conf" / "model.conf").exists():
                return True
            if (entry / "graph").exists():
                return True
        return False

    def download_piper_model(self, voice_key="zh_CN-huayan-medium",
                             progress_callback=None):
        voice = PIPER_VOICES.get(voice_key)
        if not voice:
            raise ValueError(f"Unknown piper voice: {voice_key}")

        onnx_path = PIPER_DIR / voice["onnx"]
        json_path = PIPER_DIR / voice["json"]

        if onnx_path.exists() and json_path.exists():
            return onnx_path

        base_url = voice["url_base"]
        for fname, dst in [(voice["onnx"], onnx_path), (voice["json"], json_path)]:
            if dst.exists():
                continue
            _download_file(
                base_url + fname, dst,
                progress_callback=progress_callback, label=fname,
            )

        return onnx_path

    def download_vosk_model(self, model_name=VOSK_DEFAULT_MODEL,
                            progress_callback=None):
        target_dir = VOSK_DIR / model_name
        if target_dir.exists() and any(target_dir.iterdir()):
            return target_dir

        model_info = VOSK_MODELS.get(model_name)
        if not model_info:
            raise ValueError(f"未知的Vosk模型: {model_name}")
        download_url = model_info["url"]

        zip_path = VOSK_DIR / f"{model_name}.zip"
        _download_file(
            download_url, zip_path,
            progress_callback=progress_callback, label=model_name,
        )

        if progress_callback:
            progress_callback(f"解压 {model_name} ...")

        with zipfile.ZipFile(str(zip_path), "r") as zf:
            zf.extractall(str(VOSK_DIR))

        zip_path.unlink()

        return target_dir

    def ensure_stt_model(self, progress_callback=None):
        for model_name in (VOSK_DEFAULT_MODEL, VOSK_FALLBACK_MODEL):
            model_dir = VOSK_DIR / model_name
            if model_dir.exists() and any(model_dir.iterdir()):
                return model_dir
        return self.download_vosk_model(progress_callback=progress_callback)

    def status(self):
        return {
            "pyaudio": HAS_PYAUDIO,
            "numpy": HAS_NUMPY,
            "piper": HAS_PIPER,
            "vosk": HAS_VOSK,
            "vosk_native": _VOSK_NATIVE,
            "piper_model": self.has_piper_model(),
            "vosk_model": self.has_vosk_model(),
            "tts_ready": self.check_tts_ready(),
            "stt_ready": self.check_stt_ready(),
        }

    def __repr__(self):
        s = self.status()
        return (
            f"<ModelMiddleware tts_ready={s['tts_ready']} stt_ready={s['stt_ready']} "
            f"piper={s['piper_model']} vosk={s['vosk_model']}>"
        )
