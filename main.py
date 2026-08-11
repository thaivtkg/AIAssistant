import os

if os.name == 'nt':
    os.system('color') # Kích hoạt ANSI escape sequence trên Windows
from Config.config_manager import ConfigManager
from Core.llm_engine import LlamaCppEngine
from Core.plugin_loader import PluginLoader

# Bổ sung import ở đầu file
from Core.tool_registry import ToolRegistry
from Logs.logger import setup_logger
from Memory.chat_history import SQLiteChatHistory
from Plugins.ai_chat_plugin import AIChatPlugin
from Plugins.plugin_manager import PluginManager
from Plugins.sample_plugin import SystemInfoPlugin
from Tools.tool_manager import ToolManager


def main():
    # 1. Khởi tạo Config & Logger
    config = ConfigManager()
    log_level_str = config.get("log_level", "INFO")
    log_level = getattr(__import__('logging'), log_level_str.upper(), 20)
    logger = setup_logger(level=log_level)

    logger.info("=" * 40)
    logger.info(f"Khởi động {config.get('app_name')} - {config.get('version')}")
    logger.info("=" * 40)


    # 2. Kiểm tra cấu trúc thư mục
    required_dirs = ["Core", "Tools", "Models", "Memory", "GUI", "Logs", "Plugins", "Temp"]
    for d in required_dirs:
        if not os.path.exists(d):
            os.makedirs(d)

    # 3.1 Khởi tạo Registry
    tool_registry = ToolRegistry()

    # 3.2 Nạp Plugin tự động
    plugin_loader = PluginLoader(registry=tool_registry, logger=logger)
    plugin_loader.load_plugins("Tools")

    # 3.3 Khởi tạo ToolManager
    tool_mgr = ToolManager(registry=tool_registry, logger=logger)

    # (Sanity Check - Có thể xóa bỏ nếu không cần thiết)
    # test_result = tool_mgr.execute_tool("get_system_time")
    # logger.info(f"KẾT QUẢ TEST TOOL: {test_result}")

    # 4. Khởi tạo Plugin Manager
    plugin_mgr = PluginManager(logger=logger, config=config)
    plugin_mgr.register_plugin(SystemInfoPlugin())

    # 5. Khởi tạo AI Engine & Memory
    llm_engine = LlamaCppEngine(logger=logger, config=config)
    chat_memory = SQLiteChatHistory(logger=logger)
    ai_chat_plugin = AIChatPlugin(engine=llm_engine, memory=chat_memory, tool_manager=tool_mgr)

    plugin_mgr.register_plugin(ai_chat_plugin)

    # 5. Vòng lặp Chat thử nghiệm trên Console
    logger.info("\n>>> BẮT ĐẦU PHIÊN CHAT OFFLINE (Gõ 'exit' để thoát) <<<")
    model_file = config.get("model_path", "Models/qwen3-4b.gguf")

    if not os.path.exists(model_file):
        logger.warning(f"CẢNH BÁO: Chưa tìm thấy file model tại '{model_file}'.")
        logger.warning("Vui lòng tải file .gguf và chép vào thư mục 'Models/'.")

    while True:
        try:
            user_input = input("\nBạn: ")
            if user_input.strip().lower() in ["exit", "quit"]:
                break

            # --- ĐOẠN CODE BỊ THIẾU CẦN THÊM VÀO ---
            if user_input.strip().lower() == "clear":
                ai_chat_plugin.execute(action="clear_history")
                print("\r\033[2KAI: Đã xóa toàn bộ lịch sử bộ nhớ chat!")
                continue
            # --------------------------------------

            if not user_input.strip():
                continue

            print("AI: ", end="", flush=True)

            # --- CODE ĐÃ SỬA LỖI NHẤP NHÁY ---
            # --- CODE UI TRONG MAIN.PY ---
            ui_state = {"is_thinking": False}

            def on_start():
                if not ui_state["is_thinking"]:
                    print("[Đang suy luận...] ", end="", flush=True)
                    ui_state["is_thinking"] = True

            def on_end():
                if ui_state["is_thinking"]:
                    # Dùng \r quay về đầu, in 40 dấu cách để chùi sạch, rồi lại \r in AI:
                    print("\r" + " " * 40 + "\rAI: ", end="", flush=True)
                    ui_state["is_thinking"] = False

            # -----------------------------

            # Khởi chạy luồng Chat
            for token in ai_chat_plugin.chat_stream(user_input, on_think_start=on_start, on_think_end=on_end):
                print(token, end="", flush=True)
            print()

        except KeyboardInterrupt:
            break

    # Tắt an toàn
    plugin_mgr.shutdown_all()
    logger.info("Hệ thống đã thoát an toàn.")


if __name__ == "__main__":
    main()