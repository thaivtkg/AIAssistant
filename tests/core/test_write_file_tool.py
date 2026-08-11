from unittest.mock import mock_open, patch

import pytest

from Tools.core_filesystem.file_write_tool import WriteFileTool


def test_write_file_success_lifecycle():
    tool = WriteFileTool()
    # Mock hàm open để không tạo file thật trên máy khi chạy test
    with patch("Tools.core_filesystem.file_write_tool.open", mock_open()):
        # Mock os.path.exists trả về True (Giả lập file đã được tạo thành công)
        with patch("os.path.exists", return_value=True):
            res = tool.execute(path="D:\\fake.txt", content="Hello")
            assert res["success"] is True
            assert res["verification"]["verified"] is True

def test_write_file_verification_layer_catches_silent_failure():
    tool = WriteFileTool()
    with patch("Tools.core_filesystem.file_write_tool.open", mock_open()):
        # _execute() sẽ chạy thành công (không có Exception I/O)
        # NHƯNG mock os.path.exists trả về False (Giả lập việc hệ điều hành chặn ghi đĩa âm thầm)
        with patch("os.path.exists", return_value=False):
            res = tool.execute(path="D:\\fake_silent_fail.txt", content="Hello")
            
            # Kết quả cuối cùng BẮT BUỘC phải là False
            assert res["success"] is False
            assert "chưa được ghi xuống đĩa" in res["error"]