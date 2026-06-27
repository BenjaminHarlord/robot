import json
from pathlib import Path

DPAPI_SKILLS = Path(__file__).parent.parent / "dp_api" / "skills"
LANGUAGE_INC_PATH = DPAPI_SKILLS / "language_inc.json"


class LanguageMiddleware:
    def __init__(self, lang_path=None):
        self._lang_path = Path(lang_path) if lang_path else LANGUAGE_INC_PATH
        self._en_to_zh = {}
        self._zh_to_en = {}
        self._load()

    def _load(self):
        if self._lang_path.exists():
            with open(self._lang_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        else:
            raw = {}
        self._en_to_zh = {}
        self._zh_to_en = {}
        for en, zh in raw.items():
            en_lower = en.lower()
            self._en_to_zh[en_lower] = zh
            self._zh_to_en[zh] = en_lower

    def reload(self):
        self._load()

    def to_chinese(self, word):
        if not word:
            return word
        return self._en_to_zh.get(word.lower(), word)

    def to_english(self, word):
        if not word:
            return word
        return self._zh_to_en.get(word, word)

    def is_known_label(self, word):
        if not word:
            return False
        return word.lower() in self._en_to_zh or word in self._zh_to_en

    def translate_target(self, text):
        if not text:
            return text
        if text.lower() in self._en_to_zh:
            return text.lower()
        return self._zh_to_en.get(text, text)

    def all_english_labels(self):
        return list(self._en_to_zh.keys())

    def all_chinese_labels(self):
        return list(self._zh_to_en.keys())

    def __contains__(self, word):
        return self.is_known_label(word)

    def __repr__(self):
        return f"<LanguageMiddleware labels={len(self._en_to_zh)} path={self._lang_path}>"
