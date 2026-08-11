import os
from typing import Generator, List, Dict, Any
from Core.interfaces import ILLMEngine, ILogger, IConfig

try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False


class LlamaCppEngine(ILLMEngine):
    def __init__(self, logger: ILogger, config: IConfig):
        self.logger = logger
        self.config = config
        self.llm: Any = None

    def load_model(self, model_path: str, **kwargs) -> bool:
        if not LLAMA_AVAILABLE:
            self.logger.error("Thư viện 'llama-cpp-python' chưa được cài đặt.")
            return False

        if not os.path.exists(model_path):
            self.logger.error(f"Không tìm thấy file model GGUF tại: {os.path.abspath(model_path)}")
            return False

        try:
            n_ctx = kwargs.get("n_ctx", self.config.get("n_ctx", 2048))
            n_gpu_layers = kwargs.get("n_gpu_layers", self.config.get("n_gpu_layers", 0))

            self.logger.info(f"Đang nạp model từ: {model_path} (Context: {n_ctx}, GPU Layers: {n_gpu_layers})...")
            self.llm = Llama(
                model_path=model_path,
                n_ctx=n_ctx,
                n_gpu_layers=n_gpu_layers,
                verbose=False
            )
            self.logger.info("Model AI đã được nạp thành công!")
            return True
        except Exception as e:
            self.logger.error(f"Lỗi khi nạp model: {str(e)}")
            return False

    def generate_stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        if not self.is_loaded():
            self.logger.error("Chưa nạp model AI. Không thể sinh câu trả lời.")
            yield "[Lỗi: Model AI chưa được nạp]"
            return

        try:
            # Đọc cấu hình Sampling nâng cao từ Config
            max_tokens = kwargs.get("max_tokens", self.config.get("max_tokens", 512))
            temperature = kwargs.get("temperature", self.config.get("temperature", 0.3))
            top_p = kwargs.get("top_p", self.config.get("top_p", 0.8))
            top_k = kwargs.get("top_k", self.config.get("top_k", 40))
            repeat_penalty = kwargs.get("repeat_penalty", self.config.get("repeat_penalty", 1.15)) # <-- Phạt lặp từ

            response_stream = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repeat_penalty=repeat_penalty, # <-- Ngăn chặn lặp từ hỏng
                stream=True
            )

            for chunk in response_stream:
                delta = chunk.get("choices", [{}])[0].get("delta", {})
                content = delta.get("content", "")
                if content:
                    yield content

        except Exception as e:
            self.logger.error(f"Lỗi suy luận LLM Engine: {str(e)}")
            yield f"\n[Lỗi suy luận AI: {str(e)}]"

    def is_loaded(self) -> bool:
        return self.llm is not None