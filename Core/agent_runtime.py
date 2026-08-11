import json
import re
from typing import Any, Dict, Generator, List

from Core.stream_filter import ThinkingFilter, ToolCallFilter


class AgentRuntime:
    """Lõi thực thi Agent: Xử lý logic gọi Tool, bắt lỗi JSON, và tự động phục hồi (Auto-Correction)"""

    def __init__(self, engine, tool_manager, prompt_manager):
        self.engine = engine
        self.tool_manager = tool_manager
        self.prompt_manager = prompt_manager
        self.max_retries = 3

    def execute_turn(self, user_input: str, history: List[Dict[str, str]], on_think_start=None, on_think_end=None) -> \
    Generator[str, None, None]:
        # 1. Lấy danh sách Schema và build Context ban đầu
        schemas = self.tool_manager.get_all_schemas() if self.tool_manager else []
        messages = self.prompt_manager.build_messages(history, user_input, schemas)

        full_response_to_save = ""

        # 2. Vòng lặp Agent Runtime
        for attempt in range(self.max_retries):
            raw_stream = self.engine.generate_stream(messages)

            think_filter = ThinkingFilter(on_think_start=on_think_start, on_think_end=on_think_end)
            tool_filter = ToolCallFilter()

            clean_stream = think_filter.filter_stream(raw_stream)
            final_stream = tool_filter.filter_stream(clean_stream)

            iteration_response = ""
            for chunk in final_stream:
                iteration_response += chunk
                full_response_to_save += chunk
                yield chunk

            # 3. Xử lý Logic sau khi Stream kết thúc
            if tool_filter.tool_name:
                tool_name = tool_filter.tool_name
                tool_kwargs = tool_filter.tool_kwargs

                # --- AUTO-CORRECTION 1: LỖI CÚ PHÁP JSON ---
                if tool_name == "json_parse_error":
                    error_details = tool_kwargs.get('error', 'Lỗi không xác định')
                    if self.tool_manager and self.tool_manager.logger:
                        self.tool_manager.logger.warning(f"[Runtime Recovery] JSON parse error: {error_details}. Retry {attempt+1}/{self.max_retries}")
                    
                    messages.append({"role": "assistant", "content": iteration_response})
                    messages.append({
                        "role": "system", 
                        "content": f"[RUNTIME ERROR]\nJSON gọi Tool không hợp lệ: {error_details}.\n\nHãy xuất lại đúng định dạng:\n<call>{{\"name\":\"...\",\"kwargs\":{{...}}}}</call>"
                    })
                    continue 

                # --- AUTO-CORRECTION 2: TOOL KHÔNG TỒN TẠI ---
                if self.tool_manager and not self.tool_manager.has_tool(tool_name):
                    if self.tool_manager and self.tool_manager.logger:
                        self.tool_manager.logger.warning(f"[Runtime Recovery] Hallucinated tool '{tool_name}'. Retry {attempt+1}/{self.max_retries}")
                    messages.append({"role": "assistant", "content": iteration_response})
                    messages.append({
                        "role": "system", 
                        "content": f"[RUNTIME ERROR]\nTool '{tool_name}' không tồn tại.\n\nKhông được tự tạo Tool. Hãy chọn Tool có trong danh sách được cung cấp."
                    })
                    continue
                
                # --- TOOL EXECUTION ---
                yield f"\n[⚙️ Thực thi: {tool_name}...]\n"
                try:
                    tool_result = self.tool_manager.execute_tool(tool_name, **tool_kwargs) if self.tool_manager else {
                        "error": "ToolManager offline"}
                except Exception as e:
                    tool_result = {"error": f"Exception: {str(e)}"}
                
                tool_call_str = f"<call>{json.dumps({'name': tool_name, 'kwargs': tool_kwargs}, ensure_ascii=False)}</call>"
                messages.append({"role": "assistant", "content": iteration_response + tool_call_str})
                messages.append({"role": "system", "content": f"[TOOL RESULT] ({tool_name}): {tool_result}"})

                continue
            else:
                # --- AUTO-CORRECTION 3: BẮT LỖI JSON TRẦN ---
                # Đã sửa Regex: Bắt buộc phải có cả key "name" và "kwargs" trong cùng một object. Sử dụng re.DOTALL để quét qua dòng mới (multi-line).
                if re.search(r'\{\s*"name"\s*:.*"kwargs"\s*:', iteration_response, re.DOTALL) and "<call>" not in iteration_response:
                    if self.tool_manager and self.tool_manager.logger:
                        self.tool_manager.logger.warning(f"[Runtime Recovery] Bắt được JSON trần. Đang ép AI bọc thẻ... Retry {attempt+1}/{self.max_retries}")
                    
                    messages.append({"role": "assistant", "content": iteration_response})
                    messages.append({
                        "role": "system", 
                        "content": "[RUNTIME ERROR]\nBạn đã xuất JSON trần hoặc quên bọc thẻ.\nBẮT BUỘC phải bọc chuỗi JSON gọi công cụ bên trong thẻ <call> và </call>."
                    })
                    continue 
                
                break

        return full_response_to_save