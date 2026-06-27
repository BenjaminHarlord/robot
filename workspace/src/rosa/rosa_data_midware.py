import json
import threading
from datetime import datetime
from pathlib import Path

QRS_ROOT = Path(__file__).parent.parent.parent.parent / "QRS"
DATA_PATH = QRS_ROOT / "data" / "rosa_records.json"


class DataMiddleware:
    def __init__(self, data_path=None):
        self._data_path = Path(data_path) if data_path else DATA_PATH
        self._lock = threading.Lock()
        self._ensure_file()

    def _ensure_file(self):
        self._data_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._data_path.exists():
            with open(self._data_path, "w", encoding="utf-8") as f:
                json.dump({"records": []}, f, ensure_ascii=False, indent=2)

    def _read_all(self):
        with self._lock:
            with open(self._data_path, "r", encoding="utf-8") as f:
                return json.load(f)

    def _write_all(self, data):
        with self._lock:
            with open(self._data_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    def insert_record(self, record):
        record["id"] = self._next_id()
        record["timestamp"] = record.get("timestamp") or datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        data = self._read_all()
        data["records"].append(record)
        self._write_all(data)
        return record

    def insert_interaction(self, user_input, command, decision, result):
        return self.insert_record({
            "type": "interaction",
            "user_input": user_input,
            "command": self._safe_dict(command),
            "decision": self._safe_dict(decision),
            "result": self._safe_dict(result),
        })

    def insert_detection(self, detection_info, frame_path):
        return self.insert_record({
            "type": "detection",
            "detection": detection_info,
            "frame_path": str(frame_path),
        })

    def get_records(self, limit=None, record_type=None):
        data = self._read_all()
        records = data.get("records", [])
        if record_type:
            records = [r for r in records if r.get("type") == record_type]
        if limit:
            return records[-limit:]
        return records

    def get_latest(self, record_type=None):
        records = self.get_records(record_type=record_type)
        return records[-1] if records else None

    def query(self, field, value, limit=None):
        records = self.get_records()
        results = []
        for r in records:
            if field in r and r[field] == value:
                results.append(r)
                if limit and len(results) >= limit:
                    break
        return results

    def clear(self):
        self._write_all({"records": []})

    def count(self, record_type=None):
        records = self.get_records(record_type=record_type)
        return len(records)

    def _next_id(self):
        data = self._read_all()
        records = data.get("records", [])
        if records:
            return max(r.get("id", 0) for r in records) + 1
        return 1

    def _safe_dict(self, obj):
        if obj is None:
            return {}
        if isinstance(obj, dict):
            return {k: self._safe_value(v) for k, v in obj.items()}
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        if hasattr(obj, "__dict__"):
            return self._safe_dict(vars(obj))
        return str(obj)

    def _safe_value(self, v):
        if isinstance(v, (str, int, float, bool, type(None))):
            return v
        if isinstance(v, (list, tuple)):
            return [self._safe_value(i) for i in v]
        return self._safe_dict(v)

    @property
    def data_path(self):
        return self._data_path

    def __repr__(self):
        return f"<DataMiddleware path={self._data_path} records={self.count()}>"
