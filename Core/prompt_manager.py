import json
from typing import List, Dict, Any
from Core.interfaces import IConfig, IToolManager

CALL_START = "<" + "call" + ">"
CALL_END = "<" + "/call" + ">"


class PromptManager:
    def __init__(self, config: IConfig):
        self.config = config

    def build_messages(self, history: List[Dict[str, str]], current_user_input: str,
                       tool_schemas: List[Dict[str, Any]] = None) -> List[Dict[str, str]]:

        # 1. Định danh cốt lõi
        system_prompt = self.config.get(
            "system_prompt",
            "Bạn là trợ lý AI offline bằng Tiếng Việt. Nhiệm vụ của bạn là hiểu yêu cầu, suy luận và sử dụng công cụ khi cần thiết."
        )

        # 2. Bơm Schema và Giao thức (Không chứa logic xử lý lỗi)
        if tool_schemas:
            tools_desc = "\n".join(
                [f"- {s['name']}: {s['description']} (Tham số: {json.dumps(s['parameters'], ensure_ascii=False)})"
                 for s in tool_schemas])

            system_prompt += (
                f"\n\n[HỆ THỐNG CÔNG CỤ]\nBạn có quyền sử dụng các công cụ sau:\n{tools_desc}\n\n"
                "[GIAO THỨC GỌI CÔNG CỤ]\n"
                f"Để gọi công cụ, bạn CHỈ ĐƯỢC PHÉP xuất ra đúng định dạng JSON bọc trong thẻ {CALL_START} và {CALL_END}.\n"
                "Ví dụ:\n"
                f"{CALL_START}{{\"name\": \"create_folder\", \"kwargs\": {{\"path\": \"D:\\\\\\\\Test\"}}}}{CALL_END}"
            )

        # 3. Đóng gói Context
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            messages.append(msg)
        messages.append({"role": "user", "content": current_user_input})

        return messages