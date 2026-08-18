Dưới đây là nội dung hoàn chỉnh cho file `README.md` được thiết kế chuẩn chỉnh, trực quan và bao quát toàn bộ kiến trúc cũng như cách thiết lập dự án từ Sprint 0 đến Sprint 4.

---

### 📄 File: `README.md`

* **Action:** `[ADD]` / `[MODIFY]` (Ghi đè hoặc tạo mới ở thư mục gốc của project)

```markdown
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

```

---

## 🚀 Hướng dẫn Cài đặt & Sử dụng

### 1. Yêu cầu hệ thống

* **Hệ điều hành:** Windows 10 / Windows 11 (64-bit).
* **Python:** Phiên bản `3.10` hoặc `3.11`.
* **Phần cứng khuyến nghị:** - RAM: Tối thiểu 16GB.
* GPU: NVIDIA (Khuyến nghị 6GB VRAM trở lên, ví dụ: RTX 3050, RTX 4060...) nếu muốn bật GPU Offload.



---

### 2. Cài đặt môi trường

1. **Clone repository về máy:**
```bash
git clone <URL_REPO_CUA_BAN>
cd AIAssistant

```


2. **Tạo và kích hoạt môi trường ảo (Virtual Environment):**
```powershell
python -m venv venv
.\venv\Scripts\activate

```


3. **Cài đặt các gói phụ thuộc:**
* **Cài đặt thông thường (CPU):**
```bash
pip install -r requirements.txt

```


* **(Khuyến nghị) Cài đặt hỗ trợ GPU NVIDIA (CUDA):**
```powershell
$env:CMAKE_ARGS="-DGGML_CUDA=on"
pip install --upgrade --force-reinstall --no-cache-dir llama-cpp-python

```





---

### 3. Tải Model AI

1. Tạo thư mục `Models/` (nếu chưa có).
2. Tải mô hình định dạng `.gguf` (Khuyến nghị: **Qwen2.5-Coder-7B-Instruct** hoặc **Qwen2.5-3B/4B** định dạng `Q4_K_M` hoặc `Q5_K_M`).
3. Đổi tên file hoặc cập nhật đường dẫn trong `settings.json`:
```json
{
    "model_path": "Models/qwen3-4b.gguf"
}

```



---

### 4. Cấu hình hệ thống (`settings.json`)

```json
{
    "app_name": "Offline AI Assistant",
    "version": "1.0 - Sprint 4",
    "log_level": "INFO",
    "model_path": "Models/qwen3-4b.gguf",
    "plugin_dir": "Plugins/",
    "n_ctx": 8192,
    "n_gpu_layers": 35,
    "max_tokens": 2048,
    "temperature": 0.1,
    "top_p": 0.8,
    "top_k": 40,
    "repeat_penalty": 1.15,
    "system_prompt": "Bạn là trợ lý AI offline thông minh. BẮT BUỘC phải trả lời HOÀN TOÀN bằng Tiếng Việt trong mọi tình huống."
}

```

> **Lưu ý về GPU:** Nếu bạn chạy thuần CPU, hãy đặt `"n_gpu_layers": 0`. Nếu có GPU NVIDIA rời, nâng số layer (VD: `35`) để mô hình chạy mượt mà.

---

## 🎮 Khởi chạy ứng dụng

Chạy lệnh sau tại thư mục gốc:

```powershell
python main.py

```

### Các câu lệnh và mẫu tương tác:

* **Hỏi đáp thông thường:**
```text
Bạn: Hãy giải thích thuật ngữ Big O Notation trong cấu trúc dữ liệu.

```


* **Điều khiển ứng dụng (Single-step):**
```text
Bạn: Mở giúp tôi ứng dụng Notepad.
Bạn: Kiểm tra xem ứng dụng Chrome có đang chạy không?

```


* **Kịch bản đa bước (Multi-step Agent):**
```text
Bạn: Hãy mở ứng dụng notepad. Sau đó kiểm tra xem nó đã chạy chưa, nếu có thì hãy đóng nó lại giúp tôi.

```


* **Xóa bộ nhớ đệm hội thoại:**
```text
Bạn: clear

```


* **Thoát:**
```text
Bạn: exit

```



---

## 🧪 Kiểm thử tự động (Automated Test Suite)

Dự án áp dụng chặt chẽ quy trình TDD với kiểm thử đa tầng:

1. **Chạy toàn bộ Unit & Integration Test (Chạy qua Mock, siêu nhanh và an toàn):**
```bash
pytest tests/

```


2. **Chạy bài kiểm thử vật lý với hệ điều hành Windows thực tế (Real Smoke Test):**
```bash
pytest -m windows_real -s

```


*(Test case này sẽ tự động bật ứng dụng Win32 như Character Map, xác minh HWND, đưa lên Foreground và đóng lại an toàn).*

---

## 📜 Giấy phép & Đóng góp

Dự án được xây dựng phục vụ mục đích nghiên cứu và phát triển trợ lý AI cá nhân hóa offline an toàn. Mọi đóng góp (Pull Request / Issue) đều được hoan nghênh!

```

---

Bây giờ dự án của bạn đã có một file `README.md` chuyên nghiệp để bất kỳ ai khi clone về cũng có thể thiết lập và chạy ngay mà không gặp vướng mắc. Khi bạn đã sẵn sàng, chúng ta có thể bước tiếp vào **Sprint 5: Workflow State Machine & Execution Foundation**!

```
