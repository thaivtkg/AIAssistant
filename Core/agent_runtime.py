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

                # --- AUTO-CORRECTION: LỖI CÚ PHÁP JSON ---
                if tool_name == "json_parse_error":
                    error_details = tool_kwargs.get('error', 'Unknown')
                    # CHỈ LOG, KHÔNG YIELD RA UI
                    if self.tool_manager and self.tool_manager.logger:
                        self.tool_manager.logger.warning(f"[Runtime Recovery] JSON parse error: {error_details}. Retry {attempt+1}/{self.max_retries}")
                    
                    messages.append({"role": "assistant", "content": iteration_response})
                    messages.append({
                        "role": "system", 
                        "content": f"[RUNTIME ERROR] JSON Invalid: {error_details}. Must use <call> JSON format."
                    })
                    continue 

                # --- AUTO-CORRECTION: TOOL KHÔNG TỒN TẠI ---
                if self.tool_manager and not self.tool_manager.has_tool(tool_name):
                    if self.tool_manager and self.tool_manager.logger:
                        self.tool_manager.logger.warning(f"[Runtime Recovery] Hallucinated tool '{tool_name}'. Retry {attempt+1}/{self.max_retries}")
                    # KHÔNG YIELD
                    messages.append({"role": "assistant", "content": iteration_response})
                    messages.append({
                        "role": "system", 
                        "content": f"[RUNTIME ERROR] Tool '{tool_name}' DOES NOT EXIST."
                    })
                    continue
                
                # --- THỰC THI TOOL (Sẽ cấy Verification Layer vào đây ở bước sau) ---
                yield f"\n[⚙️ Thực thi: {tool_name}...]\n"
                try:
                    tool_result = self.tool_manager.execute_tool(tool_name, **tool_kwargs) if self.tool_manager else {
                        "error": "ToolManager offline"}
                except Exception as e:
                    tool_result = {"error": f"Exception: {str(e)}"}
                
                # Nạp kết quả vào Context để AI chốt hạ hoặc làm bước tiếp theo
                tool_call_str = f"<call>{json.dumps({'name': tool_name, 'kwargs': tool_kwargs}, ensure_ascii=False)}</call>"
                messages.append({"role": "assistant", "content": iteration_response + tool_call_str})
                messages.append({"role": "system", "content": f"[TOOL RESULT] ({tool_name}): {tool_result}"})

                continue
            else:
                # --- AUTO-CORRECTION 3: BẮT LỖI JSON TRẦN ---
                # Nếu AI nói chuyện nhưng có dấu hiệu tuôn ra JSON của Tool
                if re.search(r'\{\s*"name"\s*:', iteration_response) and "<call>" not in iteration_response:
                    if self.tool_manager and self.tool_manager.logger:
                        self.tool_manager.logger.warning(f"[Runtime Recovery] Bắt được JSON trần. Đang ép AI bọc thẻ... Retry {attempt+1}/{self.max_retries}")
                    
                    messages.append({"role": "assistant", "content": iteration_response})
                    messages.append({
                        "role": "system", 
                        "content": "[RUNTIME ERROR] Bạn đã xuất JSON trần hoặc quên bọc thẻ. BẮT BUỘC phải bọc chuỗi JSON gọi công cụ bên trong thẻ <call> và </call>."
                    })
                    continue # Bắt AI sinh lại văn bản ngay lập tức
                
                break # Không có lỗi gì -> Phản hồi cho người dùng và kết thúc

        return full_response_to_save