import json
import requests

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_CHAT_PATH = "/chat/completions"


class LLMMiddleware:
    def __init__(self, base_url=None, api_key=None, model=None):
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.api_key = api_key or ""
        self.model = model or "deepseek-v4-flash"
        self.chat_path = DEFAULT_CHAT_PATH

    def configure(self, base_url=None, api_key=None, model=None, chat_path=None):
        if base_url:
            self.base_url = base_url.rstrip("/")
        if api_key:
            self.api_key = api_key
        if model:
            self.model = model
        if chat_path:
            self.chat_path = chat_path

    @property
    def is_configured(self):
        return bool(self.api_key and self.base_url)

    def chat_sync(self, messages, temperature=1.0, max_tokens=4096, extra_body=None):
        body = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "thinking": {"type": "disabled"},
        }
        if extra_body:
            body.update(extra_body)

        url = f"{self.base_url}{self.chat_path}"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
        response = requests.post(url, headers=headers, json=body, timeout=120)

        if response.status_code != 200:
            raise RuntimeError(f"API error {response.status_code}: {response.text[:300]}")

        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")

    def chat_stream(self, messages, temperature=1.0, max_tokens=4096, extra_body=None):
        body = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "thinking": {"type": "disabled"},
        }
        if extra_body:
            body.update(extra_body)

        url = f"{self.base_url}{self.chat_path}"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
        response = requests.post(url, headers=headers, json=body, stream=True, timeout=120)

        if response.status_code != 200:
            raise RuntimeError(f"API error {response.status_code}: {response.text[:300]}")

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
                except json.JSONDecodeError:
                    pass
        return full_content

    def chat_with_stream_callback(self, messages, chunk_callback, temperature=1.0, max_tokens=4096):
        body = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "thinking": {"type": "disabled"},
        }

        url = f"{self.base_url}{self.chat_path}"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
        response = requests.post(url, headers=headers, json=body, stream=True, timeout=120)

        if response.status_code != 200:
            raise RuntimeError(f"API error {response.status_code}: {response.text[:300]}")

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
                            if chunk_callback:
                                chunk_callback(content)
                except json.JSONDecodeError:
                    pass
        return full_content

    def classify(self, system_prompt, user_text, choices_map, temperature=0.0, max_tokens=16):
        content = self.chat_sync(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return content.strip()

    def __repr__(self):
        return (
            f"<LLMMiddleware base={self.base_url} model={self.model} "
            f"configured={self.is_configured}>"
        )
