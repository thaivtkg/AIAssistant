from typing import Generator, Callable, Optional
import json
# Mẹo đánh lừa IDE/Formatter: Cộng chuỗi để IDE không tưởng nhầm là thẻ HTML rồi tự xóa
START_TAG = "<" + "think" + ">"
END_TAG = "<" + "/think" + ">"


class ThinkingFilter:
    """Bộ lọc token loại bỏ thẻ suy nghĩ an toàn tuyệt đối."""

    def __init__(self, on_think_start: Optional[Callable] = None, on_think_end: Optional[Callable] = None):
        self.in_think = False
        self.buffer = ""
        self.on_start = on_think_start
        self.on_end = on_think_end

    def filter_stream(self, stream: Generator[str, None, None]) -> Generator[str, None, None]:
        for chunk in stream:
            self.buffer += chunk

            # Xử lý buffer liên tục cho đến khi cạn
            while True:
                if not self.in_think:
                    if START_TAG in self.buffer:
                        # Phân tách bằng biến START_TAG
                        parts = self.buffer.split(START_TAG, 1)
                        if parts[0]:
                            yield parts[0]
                        self.in_think = True
                        if self.on_start: self.on_start()
                        self.buffer = parts[1]
                    else:
                        # Đẩy data ra an toàn, giữ lại 10 ký tự
                        if len(self.buffer) > 10:
                            yield self.buffer[:-10]
                            self.buffer = self.buffer[-10:]
                        break
                else:
                    if END_TAG in self.buffer:
                        # Phân tách bằng biến END_TAG
                        parts = self.buffer.split(END_TAG, 1)
                        self.in_think = False
                        if self.on_end: self.on_end()
                        self.buffer = parts[1]
                    else:
                        # Vứt bỏ data thừa
                        if len(self.buffer) > 10:
                            self.buffer = self.buffer[-10:]
                        break

                        # Xử lý khi kết thúc toàn bộ luồng sinh text
        if self.in_think:
            if self.on_end: self.on_end()
            yield "\n[Hệ thống: AI suy nghĩ quá dài và bị hết Token. Vui lòng tăng max_tokens]"
        else:
            if self.buffer:
                yield self.buffer


class ToolCallFilter:
    """Bộ lọc chuyên bắt tín hiệu gọi Tool từ AI theo chuẩn <call>JSON</call>"""

    def __init__(self):
        self.buffer = ""
        self.tool_name = None
        self.tool_kwargs = {}

    def filter_stream(self, stream: Generator[str, None, None]) -> Generator[str, None, None]:
        for chunk in stream:
            self.buffer += chunk
            while True:
                if "<call>" in self.buffer:
                    parts = self.buffer.split("<call>", 1)
                    if parts[0]:
                        yield parts[0]

                    if "</call>" in parts[1]:
                        inner_parts = parts[1].split("</call>", 1)
                        json_str = inner_parts[0].strip()
                        try:
                            call_data = json.loads(json_str)
                            # BẮT BUỘC JSON phải là một Object (Dict)
                            if isinstance(call_data, dict):
                                self.tool_name = call_data.get("name", "unknown_tool")
                                self.tool_kwargs = call_data.get("kwargs", {})
                                # Ép kiểu kwargs phải là Dict để tránh lỗi **kwargs
                                if not isinstance(self.tool_kwargs, dict):
                                    self.tool_kwargs = {}
                            else:
                                raise ValueError("Dữ liệu gọi hàm không phải là JSON Object.")

                        except Exception as e:
                            # Nếu AI viết sai JSON, báo lỗi dạng nhẹ để chuyển về cho AI phân tích
                            self.tool_name = "json_parse_error"
                            self.tool_kwargs = {"raw": json_str, "error": str(e)}

                        self.buffer = ""  # Chặn luồng để thực thi Tool
                        return
                    else:
                        # Chờ có đủ thẻ đóng </call>
                        self.buffer = "<call>" + parts[1]
                        break
                else:
                    if len(self.buffer) > 10:
                        yield self.buffer[:-10]
                        self.buffer = self.buffer[-10:]
                    break
        if self.buffer:
            yield self.buffer