from datetime import datetime

from .rosa_config_midware import ConfigMiddleware
from .rosa_data_midware import DataMiddleware
from .rosa_llm_midware import LLMMiddleware
from .rosa_perception_midware import PerceptionMiddleware
from .rosa_command_midware import CommandMiddleware, CommandType
from .rosa_decision_midware import DecisionMiddleware, ActionType
from .rosa_language_midware import LanguageMiddleware


class ROSAAgent:
    def __init__(self, api_key=None, model_path=None):
        self.config = ConfigMiddleware()
        self.data = DataMiddleware()
        self.llm = LLMMiddleware()
        self.perception = PerceptionMiddleware()
        self.language = LanguageMiddleware()
        self.command = CommandMiddleware(language_middleware=self.language)
        self.decision = DecisionMiddleware()

        api_cfg = self.config.get_api_config()
        self.llm.configure(
            base_url=api_cfg["base_url"],
            api_key=api_key,
            model=api_cfg["default_model"],
            chat_path=api_cfg["chat_path"],
        )

        perc_cfg = self.config.get_perception_config()
        if model_path:
            self.perception.model_path = model_path
        elif perc_cfg.get("model_path"):
            self.perception.model_path = perc_cfg["model_path"]

        self._wire_middleware()

    def _wire_middleware(self):
        self.command.set_llm(self.llm)
        self.decision.set_llm(self.llm)

    def _llm_reply(self, system_prompt, context):
        try:
            return self.llm.chat_sync(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context},
                ],
                temperature=0.7,
                max_tokens=256,
            )
        except Exception:
            return context

    def set_api_key(self, api_key):
        self.llm.configure(api_key=api_key)

    def set_model_path(self, model_path):
        self.perception.model_path = model_path
        self.config.set("perception", "model_path", value=model_path)
        self.perception.load_model(model_path)

    def process(self, user_input):
        if not self.llm.is_configured:
            return {
                "success": False,
                "message": "请先配置 API Key",
                "action": ActionType.ERROR.value,
            }

        cmd = self.command.parse(user_input)
        context = {
            "perception": self.perception.get_latest_detection(),
        }
        decision = self.decision.decide(cmd, context)

        result = self._execute_decision(decision, cmd)

        self.data.insert_interaction(
            user_input=user_input,
            command=cmd.to_dict(),
            decision=decision.to_dict(),
            result=result,
        )

        return {
            "success": True,
            "command": cmd.to_dict(),
            "decision": decision.to_dict(),
            "result": result,
        }

    def _execute_decision(self, decision, cmd):
        action_map = {
            ActionType.DO_DETECT: self._exec_detect,
            ActionType.COUNT_OBJECTS: self._exec_count,
            ActionType.CHECK_PRESENCE: self._exec_check_presence,
            ActionType.QUERY_HISTORY: self._exec_query_history,
            ActionType.REPORT_RESULT: self._exec_report,
            ActionType.CHAT_REPLY: self._exec_chat,
            ActionType.NO_ACTION: self._exec_noop,
            ActionType.ERROR: self._exec_error,
        }

        handler = action_map.get(decision.action, self._exec_chat)
        return handler(decision, cmd)

    def _get_detection(self):
        if not self.perception.is_loaded:
            self.perception.load_model()
        latest = self.perception.get_latest_detection()
        if latest is not None:
            return latest
        return self.perception.wait_for_detection(timeout=3.0)

    def _exec_detect(self, decision, cmd):
        try:
            detection = self._get_detection()
            if detection is None:
                return {"action": "detect", "message": "暂无检测数据，请先启动实时检测"}
            frame_path = self.perception.save_frame(detection)
            self.data.insert_detection(detection.to_dict(), frame_path)

            objects_cn = ", ".join(
                self.language.to_chinese(obj) for obj in detection.objects
            ) if self.language else detection.summary

            context = f"用户问: \"{cmd.raw_text}\"。检测到 {detection.count} 个目标: {objects_cn}。"
            reply = self._llm_reply(
                "你是ROSA，一个机器人助手。根据检测结果用简短中文告知用户看到了什么。"
                "只报告检测到的物品，不要编造、不要猜测。没检测到就说没看到。",
                context,
            )
            return {
                "action": "detect",
                "detection": detection.to_dict(),
                "frame_saved": str(frame_path),
                "message": reply,
            }
        except Exception as e:
            return {"action": "detect", "error": str(e), "message": f"检测失败: {e}"}

    def _exec_count(self, decision, cmd):
        try:
            detection = self._get_detection()
            if detection is None:
                return {"action": "count", "message": "暂无检测数据，请先启动实时检测"}

            target = decision.target or cmd.target
            if target and target != "*":
                count = sum(1 for obj in detection.objects if target.lower() in obj.lower())
                target_cn = self.language.to_chinese(target) if self.language else target
            else:
                count = detection.count
                target_cn = "物品"

            context = f"用户问: \"{cmd.raw_text}\"。检测到 {count} 个{target_cn}。"
            reply = self._llm_reply(
                "你是ROSA，一个机器人助手。根据检测结果用简短中文告知用户看到了什么。"
                "只报告检测到的物品，不要编造、不要猜测。没检测到就说没看到。",
                context,
            )
            return {"action": "count", "count": count, "target": target,
                    "detection": detection.to_dict(), "message": reply}
        except Exception as e:
            return {"action": "count", "error": str(e), "message": f"统计失败: {e}"}

    def _exec_check_presence(self, decision, cmd):
        try:
            target = decision.target or cmd.target
            if not target or target == "*":
                return {"action": "check", "exists": False, "message": "请指定要查找的目标"}

            detection = self._get_detection()
            if detection is None:
                return {"action": "check", "message": "暂无检测数据，请先启动实时检测"}

            exists = detection.has_object(target)
            target_cn = self.language.to_chinese(target) if self.language else target

            context = f"用户问: \"{cmd.raw_text}\"。检测结果: {'发现了' if exists else '没有发现'}{target_cn}。"
            reply = self._llm_reply(
                "你是ROSA，一个机器人助手。根据检测结果用简短中文告知用户看到了什么。"
                "只报告检测到的物品，不要编造、不要猜测。没检测到就说没看到。",
                context,
            )
            return {"action": "check", "target": target, "exists": exists,
                    "detection": detection.to_dict(), "message": reply}
        except Exception as e:
            return {"action": "check", "error": str(e), "message": f"检查失败: {e}"}

    def _exec_query_history(self, decision, cmd):
        records = self.data.get_records(limit=10, record_type="detection")
        return {"action": "history", "records": records,
                "count": len(records), "message": f"最近 {len(records)} 条检测记录"}

    def _exec_report(self, decision, cmd):
        last = self.perception.get_latest_detection()
        if last:
            info = last.to_dict()
        else:
            latest_rec = self.data.get_latest(record_type="detection")
            info = latest_rec.get("detection", {}) if latest_rec else {}
        return {"action": "report", "result": info, "message": "已汇报感知结果"}

    def _exec_chat(self, decision, cmd):
        try:
            reply = self.llm.chat_sync(
                messages=[
                    {"role": "system", "content": "你是ROSA机器人智能助手，帮助用户理解环境和执行检测任务。"},
                    {"role": "user", "content": cmd.raw_text},
                ],
                temperature=self.config.get("api", "temperature", default=1.0),
                max_tokens=self.config.get("api", "max_tokens", default=4096),
            )
            return {"action": "chat", "reply": reply, "message": "对话完成"}
        except Exception as e:
            return {"action": "chat", "error": str(e), "message": f"对话失败: {e}"}

    def _exec_noop(self, decision, cmd):
        return {"action": "noop", "message": "无需执行操作"}

    def _exec_error(self, decision, cmd):
        return {"action": "error", "message": decision.reasoning}

    def chat_reply_stream(self, message, chunk_callback=None):
        try:
            messages = [
                {"role": "system", "content": "你是ROSA机器人智能助手。"},
                {"role": "user", "content": message},
            ]
            if chunk_callback:
                return self.llm.chat_with_stream_callback(messages, chunk_callback)
            return self.llm.chat_stream(messages)
        except Exception as e:
            return f"[错误] {e}"

    def get_status(self):
        return {
            "llm_configured": self.llm.is_configured,
            "model_loaded": self.perception.is_loaded,
            "model_path": self.perception.model_path,
            "records_count": self.data.count(),
            "base_url": self.llm.base_url,
            "default_model": self.llm.model,
        }

    def get_history(self, limit=10):
        return self.data.get_records(limit=limit, record_type="interaction")

    def clear_history(self):
        self.data.clear()
