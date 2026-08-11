import os
import json
from typing import Any, Dict, Generator
from Core.base_plugin import BasePlugin
from Core.interfaces import ILLMEngine, IChatHistory, IToolManager
from Core.prompt_manager import PromptManager
from Core.stream_filter import ThinkingFilter, ToolCallFilter
from Core.agent_runtime import AgentRuntime


class AIChatPlugin(BasePlugin):
    def __init__(self, engine: ILLMEngine, memory: IChatHistory, tool_manager: IToolManager = None):
        super().__init__(name="AIChat", version="1.2.0")
        self.engine = engine
        self.memory = memory
        self.tool_manager = tool_manager
        self.prompt_manager = None
        self.runtime = None

    def initialize(self) -> bool:
        if self.config:
            self.prompt_manager = PromptManager(self.config)

        # Khởi tạo Agent Runtime
        self.runtime = AgentRuntime(self.engine, self.tool_manager, self.prompt_manager)

        model_path = self.config.get("model_path", "Models/qwen3-4b.gguf") if self.config else "Models/qwen3-4b.gguf"
        if not self.engine.is_loaded():
            if os.path.exists(model_path):
                self.engine.load_model(model_path)
            else:
                if self.logger:
                    self.logger.warning(f"[{self.name}] Chưa có model tại '{model_path}'.")
        return True

    def chat_stream(self, user_input: str, on_think_start=None, on_think_end=None) -> Generator[str, None, None]:
        recent_history = self.memory.get_recent_messages(limit=6)

        # Bàn giao toàn bộ vòng lặp thực thi cho AgentRuntime
        full_response = yield from self.runtime.execute_turn(
            user_input=user_input,
            history=recent_history,
            on_think_start=on_think_start,
            on_think_end=on_think_end
        )

        if isinstance(full_response, str) and full_response.strip():
            self.memory.add_message("user", user_input)
            self.memory.add_message("assistant", full_response)

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        if action == "clear_history":
            self.memory.clear()
            return {"success": True, "message": "Đã xóa toàn bộ lịch sử trò chuyện."}
        elif action == "get_history":
            limit = kwargs.get("limit", 10)
            return {"success": True, "history": self.memory.get_recent_messages(limit)}
        return {"success": False, "error": f"Hành động '{action}' không được hỗ trợ."}

    def shutdown(self) -> None:
        if self.logger:
            self.logger.info(f"[{self.name}] Đã ngắt kết nối Plugin AI Chat.")