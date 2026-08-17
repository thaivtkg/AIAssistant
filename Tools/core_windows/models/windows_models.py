from dataclasses import dataclass
from typing import Optional

@dataclass
class ProcessInfo:
    pid: int
    name: str
    exe: Optional[str] = None
    status: Optional[str] = None
    memory_mb: Optional[float] = 0.0

@dataclass
class ApplicationInfo:
    app_id: str
    name: str
    executable_path: str

@dataclass
class WindowInfo:
    hwnd: int
    title: str
    pid: int
    visible: bool
    minimized: bool