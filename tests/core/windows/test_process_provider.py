import pytest
import psutil
from unittest.mock import patch, MagicMock
from Tools.core_windows.providers.process_provider import ProcessProvider

@patch("psutil.Process")
def test_get_process_raises_not_found(mock_process):
    # Mock OS ném NoSuchProcess
    mock_process.side_effect = psutil.NoSuchProcess(pid=999)
    provider = ProcessProvider()
    
    with pytest.raises(ProcessLookupError) as exc:
        provider.get_process(999)
    assert "NOT_FOUND" in str(exc.value)

@patch("psutil.Process")
def test_get_process_raises_access_denied(mock_process):
    mock_process.side_effect = psutil.AccessDenied(pid=1)
    provider = ProcessProvider()
    
    with pytest.raises(PermissionError) as exc:
        provider.get_process(1)
    assert "ACCESS_DENIED" in str(exc.value)