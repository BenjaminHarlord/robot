import json
import re
from enum import Enum


class CommandType(Enum):
    CHAT = "chat"
    DETECT = "detect"
    INQUIRE = "inquire"
    ACTION = "action"
    UNKNOWN = "unknown"


class ParsedCommand:
    def __init__(self, raw_text, cmd_type, intent, target="", params=None, confidence=0.0):
        self.raw_text = raw_text
        self.cmd_type = cmd_type if isinstance(cmd_type, CommandType) else CommandType(cmd_type)
        self.intent = intent
        self.target = target
        self.params = params or {}
        self.confidence = confidence

    def to_dict(self):
        return {
            "raw_text": self.raw_text,
            "cmd_type": self.cmd_type.value,
            "intent": self.intent,
            "target": self.target,
            "params": self.params,
            "confidence": self.confidence,
        }

    @property
    def is_visual_task(self):
        return self.cmd_type == CommandType.DETECT

    @property
    def is_chat_task(self):
        return self.cmd_type in (CommandType.CHAT, CommandType.INQUIRE)

    @property
    def is_action_task(self):
        return self.cmd_type == CommandType.ACTION

    def __repr__(self):
        return (
            f"<ParsedCommand type={self.cmd_type.value} "
            f"intent='{self.intent}' target='{self.target}' "
            f"confidence={self.confidence:.2f}>"
        )


COMMAND_PARSE_SYSTEM_PROMPT = """你是一个机器人指令解析器。分析用户输入，输出严格的JSON格式。

命令类型 cmd_type 取值:
- "detect": 需要摄像头进行目标检测、物体识别、查看周围环境
- "inquire": 询问检测结果、统计物体数量、查询历史检测记录
- "chat": 普通对话、知识问答、闲聊
- "action": 需要执行具体动作
- "unknown": 无法分类

JSON输出格式:
{
  "cmd_type": "detect/chat/inquire/action/unknown",
  "intent": "简短意图描述",
  "target": "用户关注的目标对象",
  "params": {},
  "confidence": 0.0~1.0
}

仅输出JSON，不包含其他文字。"""


class CommandMiddleware:
    def __init__(self, llm_middleware=None):
        self._llm = llm_middleware

    def set_llm(self, llm_middleware):
        self._llm = llm_middleware

    def parse(self, text):
        text = text.strip()
        if not text:
            return ParsedCommand(
                raw_text=text, cmd_type=CommandType.UNKNOWN,
                intent="空输入", confidence=0.0,
            )

        rule_result = self._rule_parse(text)
        if rule_result and rule_result.confidence >= 0.9:
            return rule_result

        if self._llm and self._llm.is_configured:
            return self._llm_parse(text)

        return self._fallback_parse(text)

    def _rule_parse(self, text):
        text_lower = text.lower()

        detect_keywords = ["看看", "识别", "检测", "有什么", "看到什么", "扫一扫", "扫描"]
        inquire_keywords = ["几个", "多少", "统计", "数一数", "有没有", "是否", "在吗", "存在"]

        target = self._extract_target(text)

        for kw in detect_keywords:
            if kw in text_lower:
                for iq in inquire_keywords:
                    if iq in text_lower:
                        return ParsedCommand(
                            raw_text=text, cmd_type=CommandType.INQUIRE,
                            intent=f"查询: {kw}", target=target, confidence=0.92,
                        )
                return ParsedCommand(
                    raw_text=text, cmd_type=CommandType.DETECT,
                    intent=f"检测触发: {kw}", target=target, confidence=0.95,
                )

        for iq in inquire_keywords:
            if iq in text_lower:
                return ParsedCommand(
                    raw_text=text, cmd_type=CommandType.INQUIRE,
                    intent="查询统计", target=target, confidence=0.85,
                )

        return None

    def _extract_target(self, text):
        targets = ["人", "person", "车", "car", "猫", "cat", "狗", "dog",
                    "杯子", "cup", "瓶子", "bottle", "手机", "cell phone",
                    "电脑", "laptop", "椅子", "chair", "桌子", "table",
                    "书", "book", "背包", "backpack", "水果", "fruit"]
        for t in targets:
            if t in text.lower():
                return t
        return "*"

    def _llm_parse(self, text):
        try:
            content = self._llm.classify(
                COMMAND_PARSE_SYSTEM_PROMPT, text, {}, max_tokens=256
            )
            content = self._clean_json(content)
            parsed = json.loads(content)
            return ParsedCommand(
                raw_text=text,
                cmd_type=parsed.get("cmd_type", "chat"),
                intent=parsed.get("intent", ""),
                target=parsed.get("target", ""),
                params=parsed.get("params", {}),
                confidence=float(parsed.get("confidence", 0.5)),
            )
        except Exception:
            return self._fallback_parse(text)

    def _clean_json(self, text):
        text = text.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        return text

    def _fallback_parse(self, text):
        return ParsedCommand(
            raw_text=text, cmd_type=CommandType.CHAT,
            intent="普通对话", target="", confidence=0.3,
        )

    def __repr__(self):
        return f"<CommandMiddleware llm_configured={bool(self._llm and self._llm.is_configured)}>"
