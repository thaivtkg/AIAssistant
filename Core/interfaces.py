from abc import ABC, abstractmethod
from typing import Any, Dict, Generator, List


# --- CODE CŨ GIỮ NGUYÊN ---
class ILogger(ABC):
    @abstractmethod
    def info(self, message: str) -> None: pass

    @abstractmethod
    def warning(self, message: str) -> None: pass

    @abstractmethod
    def error(self, message: str) -> None: pass

    @abstractmethod
    def debug(self, message: str) -> None: pass


class IConfig(ABC):
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any: pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None: pass


# --- BỔ SUNG CODE MỚI CHO SPRINT 1 ---
class ILLMEngine(ABC):
    """Interface cho mọi LLM Engine (LlamaCpp, Ollama, vLLM...)"""

    @abstractmethod
    def load_model(self, model_path: str, **kwargs) -> bool: pass

    @abstractmethod
    def generate_stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]: pass

    @abstractmethod
    def is_loaded(self) -> bool: pass


class IChatHistory(ABC):
    """Interface cho quản lý bộ nhớ lịch sử chat (SQLite, JSON, RAM...)"""

    @abstractmethod
    def add_message(self, role: str, content: str) -> None: pass

    @abstractmethod
    def get_recent_messages(self, limit: int = 10) -> List[Dict[str, str]]: pass

    @abstractmethod
    def clear(self) -> None: pass

class IToolManager(ABC):
    """Interface trừu tượng hóa cho Tool Engine"""
    @abstractmethod
    def get_all_schemas(self) -> List[Dict[str, Any]]: pass

    @abstractmethod
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]: pass