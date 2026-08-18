# 🤖 Offline AI Assistant (Windows OS Agent)

Hệ thống trợ lý AI Offline chạy mô hình cục bộ (Local LLM), có khả năng suy luận đa bước (Multi-step Agent), quản lý cửa sổ, điều khiển tiến trình hệ điều hành Windows an toàn và hỗ trợ kiến trúc Plugin mở rộng.

---

## 🌟 Tính năng nổi bật

- 🧠 **Chạy 100% Offline & Riêng tư:** Chạy mô hình ngôn ngữ lớn (GGUF) trực tiếp trên phần cứng máy tính (hỗ trợ tăng tốc GPU qua CUDA/llama-cpp-python).
- 🛡️ **Ranh giới Bảo mật Chặt chẽ (Security Boundaries):**
  - Khởi chạy ứng dụng qua **Allowlist** với đường dẫn tuyệt đối (Absolute Trusted Path). Chống tấn công qua shell/CMD/PowerShell hoặc PATH hijacking.
  - Chống tắt nhầm các tiến trình hệ thống quan trọng (**System Process Denylist**).
  - Đóng ứng dụng an toàn qua tín hiệu `WM_CLOSE` (Graceful Close), nói **KHÔNG** với Force Kill bừa bãi.
  - Cơ chế xin quyền tương tác nguy hiểm (**User Permission Loop [Y/N]**).
- 🔍 **Lớp Hậu kiểm Hệ điều hành (Verification Layer):**
  - Tự động kiểm tra trạng thái thực của HĐH sau khi gọi Tool (tìm PID mới, kiểm tra cửa sổ trồi lên Foreground, xác minh HWND biến mất).
- ⚡ **Quản lý Context & Chống tràn Token:**
  - Lọc và phân trang dữ liệu tiến trình/cửa sổ trực tiếp từ OS Provider trước khi nạp vào bộ nhớ AI.
- 🔌 **Plugin Architecture & Auto-Discovery:** Tự động phát hiện và đăng ký Tool thông qua `manifest.json`.

---

## 🏗️ Cấu trúc thư mục dự án

```text
AIAssistant/
├── Config/             # Quản lý file cấu hình hệ thống
├── Core/               # Kiến trúc cốt lõi: LLM Engine, Tool Registry, Agent Runtime, Workflow
├── Logs/               # Hệ thống Logging cục bộ
├── Memory/             # Quản lý bộ nhớ hội thoại (SQLite Chat History)
├── Models/             # Nơi chứa các file mô hình LLM (*.gguf)
├── Plugins/            # Các plugin mở rộng chức năng
├── Tools/              # Bộ công cụ Agent (Filesystem, Core Windows Tools)
│   └── core_windows/   # Windows Manager, Providers (Process, App, Window) & 7 Windows Tools
├── tests/              # Test Suites (Unit Tests, Integration Tests, Real OS Smoke Tests)
├── main.py             # Điểm khởi chạy ứng dụng
├── pytest.ini          # Cấu hình Pytest & Custom Markers
├── requirements.txt    # Danh sách thư viện phụ thuộc
├── settings.json       # Cấu hình tham số Model, Context, Logging
└── README.md
