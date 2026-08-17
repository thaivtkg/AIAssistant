import pytest
from Tools.core_filesystem.security import FileSecurityManager

def test_security_allowed_paths():
    assert FileSecurityManager.is_safe_path("D:\\MyDocs\\test.txt") is True
    assert FileSecurityManager.is_safe_path("C:\\Users\\Public\\test.txt") is True

def test_security_denies_path_traversal():
    assert FileSecurityManager.is_safe_path("D:\\MyDocs\\..\\..\\Windows\\System32") is False
    assert FileSecurityManager.is_safe_path("D:\\MyDocs/../../Windows") is False

def test_security_denies_system_directories():
    assert FileSecurityManager.is_safe_path("C:\\Windows\\System32\\cmd.exe") is False
    assert FileSecurityManager.is_safe_path("C:\\Program Files\\app.exe") is False
    assert FileSecurityManager.is_safe_path("C:\\") is False # Không được thao tác root C