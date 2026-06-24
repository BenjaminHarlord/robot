import json
import re
from enum import Enum


class ActionType(Enum):
    NO_ACTION = "no_action"
    DO_DETECT = "do_detect"
    QUERY_HISTORY = "query_history"
    COUNT_OBJECTS = "count_objects"
    CHECK_PRESENCE = "check_presence"
    CHAT_REPLY = "chat_reply"
    REPORT_RESULT = "report_result"
    ERROR = "error"


class Decision:
    def __init__(self, action, target="", params=None, reasoning="", priority=5):
        self.action = action if isinstance(action, ActionType) else ActionType(action)
        self.target = target
        self.params = params or {}
        self.reasoning = reasoning
        self.priority = priority

    def to_dict(self):
        return {
            "action": self.action.value,
            "target": self.target,
            "params": self.params,
            "reasoning": self.reasoning,
            "priority": self.priority,
        }

    def __repr__(self):
        return f"<Decision {self.action.value} target='{self.target}' p={self.priority}>"


DECISION_RULES = [
    {
        "name": "YOLO检测触发",
        "when_cmd_type": "detect",
        "action": "do_detect",
        "priority": 8,
    },
    {
        "name": "存在性检查",
        "when_cmd_type": "inquire",
        "when_target_not_empty": True,
        "when_intent_contains": ["有没有", "是否", "在吗", "存在", "查询"],
        "action": "check_presence",
        "priority": 7,
    },
    {
        "name": "对象计数",
        "when_cmd_type": "inquire",
        "when_target_not_empty": True,
        "action": "count_objects",
        "priority": 7,
    },
    {
        "name": "历史记录查询",
        "when_cmd_type": "inquire",
        "when_target_empty": True,
        "action": "query_history",
        "priority": 6,
    },
    {
        "name": "结果报告",
        "when_cmd_type": "action",
        "when_intent_contains": ["报告", "汇报", "总结"],
        "action": "report_result",
        "priority": 6,
    },
    {
        "name": "普通对话",
        "when_cmd_type": "chat",
        "action": "chat_reply",
        "priority": 5,
    },
]

DECISION_LLM_PROMPT = """你是一个机器人决策引擎。根据解析后的指令和当前感知结果，输出下一步行动。
输出严格JSON:
{
  "action": "do_detect|query_history|count_objects|check_presence|chat_reply|report_result|no_action",
  "target": "目标对象",
  "params": {},
  "reasoning": "决策理由",
  "confidence": 0.0~1.0
}
仅输出JSON。"""


class DecisionMiddleware:
    def __init__(self, llm_middleware=None, rules=None):
        self._llm = llm_middleware
        self._rules = rules or DECISION_RULES

    def set_llm(self, llm_middleware):
        self._llm = llm_middleware

    def decide(self, parsed_command, context=None):
        if parsed_command is None:
            return Decision(action=ActionType.ERROR, reasoning="无法解析指令", priority=10)

        context = context or {}

        for rule in self._rules:
            if self._match_rule(rule, parsed_command, context):
                return Decision(
                    action=rule["action"],
                    target=parsed_command.target,
                    params={**rule.get("params", {}), **parsed_command.params},
                    reasoning=f"规则: {rule['name']}",
                    priority=rule.get("priority", 5),
                )

        if self._llm and self._llm.is_configured:
            llm_decision = self._llm_decide(parsed_command, context)
            if llm_decision:
                return llm_decision

        return Decision(action=ActionType.CHAT_REPLY, reasoning="默认对话", priority=3)

    def _match_rule(self, rule, cmd, context):
        when_type = rule.get("when_cmd_type")
        if when_type and when_type != cmd.cmd_type.value:
            return False

        when_target_not_empty = rule.get("when_target_not_empty")
        if when_target_not_empty is True and not cmd.target:
            return False

        when_target_empty = rule.get("when_target_empty")
        if when_target_empty is True and cmd.target:
            return False

        intent_contains = rule.get("when_intent_contains", [])
        if intent_contains:
            return any(ic in cmd.intent for ic in intent_contains)

        if "when_intent_contains" in rule:
            return False

        return True

    def _llm_decide(self, cmd, context):
        try:
            perception_dict = {}
            detection = context.get("perception")
            if hasattr(detection, "to_dict"):
                perception_dict = detection.to_dict()
            elif isinstance(detection, dict):
                perception_dict = detection

            user_prompt = (
                f"指令: intent={cmd.intent}, target={cmd.target}, type={cmd.cmd_type.value}\n"
                f"感知: {json.dumps(perception_dict, ensure_ascii=False)}\n"
                f"上下文: {json.dumps({k: v for k, v in context.items() if k != 'perception'}, ensure_ascii=False, default=str)}"
            )

            content = self._llm.classify(DECISION_LLM_PROMPT, user_prompt, {}, max_tokens=256)
            content = re.sub(r"^```(?:json)?\s*|```$", "", content.strip()).strip()
            parsed = json.loads(content)

            return Decision(
                action=ActionType(parsed.get("action", "chat_reply")),
                target=parsed.get("target", ""),
                params=parsed.get("params", {}),
                reasoning=f"LLM: {parsed.get('reasoning', '')}",
                priority=int(float(parsed.get("confidence", 0.5)) * 10),
            )
        except Exception:
            return None

    def __repr__(self):
        return f"<DecisionMiddleware rules={len(self._rules)} llm={bool(self._llm and self._llm.is_configured)}>"
