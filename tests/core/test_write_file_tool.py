import pytest
from unittest.mock import patch, mock_open
from Tools.core_filesystem.file_write_tool import WriteFileTool

def test_write_file_success_lifecycle():
    tool = WriteFileTool()
    
    # Mock hàm open để không tạo file thật trên đĩa
    with patch("Tools.core_filesystem.file_write_tool.open", mock_open()):
        # Mock bảo mật và kiểm tra tồn tại
        with patch("Tools.core_filesystem.security.FileSecurityManager.is_safe_path", return_value=True):
            with patch("os.path.exists", return_value=True):
                res = tool.execute(path="D:\\fake_test.txt", content="Hello")
                
                assert res["success"] is True
                assert res["verification"]["verified"] is True

def test_write_file_silent_failure_caught_by_verify():
    tool = WriteFileTool()
    
    with patch("Tools.core_filesystem.file_write_tool.open", mock_open()):
        with patch("Tools.core_filesystem.security.FileSecurityManager.is_safe_path", return_value=True):
            # CỐ TÌNH GIẢ LẬP LỖI HỆ ĐIỀU HÀNH:
            # _execute sẽ chạy thành công (không ném Exception)
            # Nhưng os.path.exists trả về False (file thực tế không xuất hiện)
            with patch("os.path.exists", return_value=False):
                res = tool.execute(path="D:\\fake_silent_fail.txt", content="Hello")
                
                # Verification Layer phải lật ngược kết quả thành False
                assert res["success"] is False
                assert "chưa được ghi xuống đĩa" in res["error"]