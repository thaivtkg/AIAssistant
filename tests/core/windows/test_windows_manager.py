import pytest
import time
from Tools.core_windows.windows_manager import WindowsManager

def test_wait_until_success_immediately():
    manager = WindowsManager()
    # Điều kiện đúng ngay lập tức
    result = manager.wait_until(lambda: True, timeout=1.0)
    assert result is True

def test_wait_until_timeout_failure():
    manager = WindowsManager()
    start = time.time()
    # Điều kiện luôn sai -> Ép phải chờ hết timeout
    result = manager.wait_until(lambda: False, timeout=0.5, interval=0.1)
    end = time.time()
    
    assert result is False
    assert (end - start) >= 0.5 # Thời gian chạy phải bằng hoặc lớn hơn timeout