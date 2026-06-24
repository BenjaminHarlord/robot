import json
from pathlib import Path

QRS_ROOT = Path(__file__).resolve().parent.parent.parent.parent / "QRS"
CONFIG_PATH = QRS_ROOT / "config" / "rosa_config.json"

DEFAULT_CONFIG = {
    "agent": {"name": "ROSA Agent", "version": "1.0.0"},
    "api": {
        "base_url": "https://api.deepseek.com",
        "chat_path": "/chat/completions",
        "default_model": "deepseek-v4-flash",
        "temperature": 1.0,
        "max_tokens": 4096,
    },
    "perception": {
        "model_path": "",
        "confidence_threshold": 0.5,
        "device": 0,
        "save_frame_interval": 10,
    },
    "mission": {"description": "", "target": "", "actions": []},
}


class ConfigMiddleware:
    def __init__(self, config_path=None):
        self._config_path = Path(config_path) if config_path else CONFIG_PATH
        self._config = {}
        self._load()

    def _load(self):
        if self._config_path.exists():
            with open(self._config_path, "r", encoding="utf-8") as f:
                self._config = json.load(f)
        else:
            self._config = DEFAULT_CONFIG.copy()
            self._save()

    def _save(self):
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._config_path, "w", encoding="utf-8") as f:
            json.dump(self._config, f, ensure_ascii=False, indent=4)

    def get(self, *keys, default=None):
        d = self._config
        for k in keys:
            if isinstance(d, dict):
                d = d.get(k)
            else:
                return default
        return d if d is not None else default

    def set(self, *keys, value):
        d = self._config
        for k in keys[:-1]:
            if k not in d:
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value
        self._save()

    def get_api_config(self):
        return {
            "base_url": self.get("api", "base_url"),
            "chat_path": self.get("api", "chat_path"),
            "default_model": self.get("api", "default_model"),
            "temperature": self.get("api", "temperature"),
            "max_tokens": self.get("api", "max_tokens"),
        }

    def get_perception_config(self):
        return {
            "model_path": self.get("perception", "model_path"),
            "confidence_threshold": self.get("perception", "confidence_threshold"),
            "device": self.get("perception", "device"),
            "save_frame_interval": self.get("perception", "save_frame_interval"),
        }

    def get_mission(self):
        return self.get("mission", default={})

    def set_mission(self, description="", target="", actions=None):
        self.set("mission", value={
            "description": description,
            "target": target,
            "actions": actions or [],
        })

    def get_qrs_path(self, subdir):
        return QRS_ROOT / subdir

    @property
    def qrs_root(self):
        return QRS_ROOT

    @property
    def config_root(self):
        return QRS_ROOT / "config"

    @property
    def data_root(self):
        return QRS_ROOT / "data"

    @property
    def images_root(self):
        return QRS_ROOT / "images"

    @property
    def models_root(self):
        return QRS_ROOT / "models"

    def to_dict(self):
        return self._config.copy()

    def __repr__(self):
        return f"<ConfigMiddleware path={self._config_path}>"
