import hashlib
import os
import re
from pathlib import Path
from urllib.parse import urlparse

import requests
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, QObject
from PyQt6.QtGui import QPixmap

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = SCRIPT_DIR / "dp_image_research.toml"

IMAGE_EXT_PAT = re.compile(r"\.(png|jpe?g|gif|webp|bmp|svg)(\?.*)?$", re.IGNORECASE)
MARKDOWN_IMG_PAT = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
RAW_URL_PAT = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)


def extract_image_urls(text, parse_markdown=True, parse_raw=True):
    urls = []
    if parse_markdown:
        for match in MARKDOWN_IMG_PAT.finditer(text):
            urls.append(match.group(2))
    if parse_raw:
        for match in RAW_URL_PAT.finditer(text):
            url = match.group(0).rstrip(".,;:!?)")
            if IMAGE_EXT_PAT.search(url) and url not in urls:
                urls.append(url)
    return urls


class ImageResearchConfig:
    def __init__(self, config_path=None):
        self.config_path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
        self.data = {}
        if tomllib and self.config_path.exists():
            with open(self.config_path, "rb") as f:
                self.data = tomllib.load(f)

    def _get(self, *keys, default=None):
        d = self.data
        for k in keys:
            if isinstance(d, dict):
                d = d.get(k)
            else:
                return default
        return d if d is not None else default

    @property
    def enabled(self):
        return self._get("image_display", "enabled", default=True)

    @property
    def max_images(self):
        return self._get("image_display", "max_images", default=12)

    @property
    def allowed_extensions(self):
        return self._get("image_display", "allowed_extensions",
                         default=[".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"])

    @property
    def cache_dir(self):
        return Path(self._get("cache", "dir", default="/tmp/dp_image_cache"))

    @property
    def timeout(self):
        return self._get("image_search", "timeout_seconds", default=30)

    @property
    def user_agent(self):
        return self._get("image_search", "user_agent", default="DP-Chat-ImageMiddleware/1.0")

    @property
    def parse_markdown_images(self):
        return self._get("stream", "parse_markdown_images", default=True)

    @property
    def parse_raw_urls(self):
        return self._get("stream", "parse_raw_urls", default=True)

    @property
    def debounce_ms(self):
        return self._get("stream", "debounce_ms", default=500)


class ImageFetcher(QThread):
    fetched = pyqtSignal(str, QPixmap, str)
    error = pyqtSignal(str, str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self._urls = []
        self._running = True

    def set_urls(self, urls):
        self._urls = list(urls)

    def run(self):
        for url in self._urls:
            if not self._running:
                break
            try:
                pixmap = self._download(url)
                if pixmap:
                    caption = os.path.basename(urlparse(url).path) or url
                    self.fetched.emit(url, pixmap, caption)
            except Exception as e:
                self.error.emit(url, str(e))
        self._urls = []

    def _download(self, url):
        cache_dir = self.config.cache_dir
        cache_dir.mkdir(parents=True, exist_ok=True)
        url_hash = hashlib.md5(url.encode()).hexdigest()
        ext = ".png"
        path_lower = urlparse(url).path.lower()
        for e in self.config.allowed_extensions:
            if path_lower.endswith(e):
                ext = e
                break
        cache_file = cache_dir / f"{url_hash}{ext}"

        if cache_file.exists() and cache_file.stat().st_size > 0:
            return QPixmap(str(cache_file))

        headers = {"User-Agent": self.config.user_agent}
        resp = requests.get(url, headers=headers, timeout=self.config.timeout, stream=True)
        if resp.status_code != 200:
            return None
        content_type = resp.headers.get("content-type", "")
        if "image" not in content_type and not any(
            url.lower().endswith(e) for e in self.config.allowed_extensions
        ):
            return None

        data = resp.content
        with open(cache_file, "wb") as f:
            f.write(data)
        return QPixmap(str(cache_file))

    def stop(self):
        self._running = False


class ChatImageMiddleware(QObject):
    image_urls_detected = pyqtSignal(list)
    image_fetched = pyqtSignal(str, QPixmap, str)
    image_error = pyqtSignal(str, str)

    def __init__(self, config_path=None):
        super().__init__()
        self.config = ImageResearchConfig(config_path)

        self._fetcher = ImageFetcher(self.config)
        self._fetcher.fetched.connect(self._on_image_fetched)
        self._fetcher.error.connect(self._on_image_error)

        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._flush_pending)

        self._pending_urls = set()
        self._seen_urls = set()

    def process_chunk(self, text):
        if not self.config.enabled:
            return []

        urls = []
        if self.config.parse_markdown_images:
            for match in MARKDOWN_IMG_PAT.finditer(text):
                urls.append((match.group(2), match.group(1)))

        if self.config.parse_raw_urls:
            for match in RAW_URL_PAT.finditer(text):
                url = match.group(0).rstrip(".,;:!?)")
                if IMAGE_EXT_PAT.search(url):
                    known = [u for u, _ in urls]
                    if url not in known:
                        urls.append((url, ""))

        new_urls = []
        for url, caption in urls:
            if url not in self._seen_urls:
                self._seen_urls.add(url)
                self._pending_urls.add(url)
                new_urls.append(url)

        if new_urls:
            self.image_urls_detected.emit(new_urls)
            if self.config.debounce_ms > 0:
                self._debounce_timer.start(self.config.debounce_ms)
            else:
                self._flush_pending()

        return new_urls

    def _flush_pending(self):
        if not self._pending_urls:
            return
        urls = list(self._pending_urls)
        self._pending_urls.clear()
        self._fetcher.set_urls(urls)
        if not self._fetcher.isRunning():
            self._fetcher.start()
        else:
            self._fetcher.set_urls(urls)

    def _on_image_fetched(self, url, pixmap, caption):
        self.image_fetched.emit(url, pixmap, caption)

    def _on_image_error(self, url, err):
        self.image_error.emit(url, err)

    def reset(self):
        self._seen_urls.clear()
        self._pending_urls.clear()
        self._debounce_timer.stop()

    def shutdown(self):
        self._debounce_timer.stop()
        self._fetcher.stop()
        self._fetcher.wait(3000)
