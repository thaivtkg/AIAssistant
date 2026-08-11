from abc import ABC, abstractmethod
from typing import Any, Dict
from Core.interfaces import ILogger, IConfig

class BasePlugin(ABC):
    """
    Lớp cơ sở cho mọi Plugin trong hệ thống.
    Tuân thủ Open/Closed và Liskov Substitution Principle.
    """
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.logger: ILogger | None = None
        self.config: IConfig | None = None

    def setup(self, logger: ILogger, config: IConfig) -> None:
        """Inject phụ thuộc từ Core vào Plugin (Dependency Injection)"""
        self.logger = logger
        self.config = config

    @abstractmethod
    def initialize(self) -> bool:
        """Khởi tạo tài nguyên/kết nối của Plugin. Trả về True nếu thành công."""
        pass

    @abstractmethod
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Thực thi một action của plugin.
        Ví dụ: action="create_folder", path="C:/Test"
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Dọn dẹp bộ nhớ/tài nguyên khi thoát ứng dụng."""
        pass