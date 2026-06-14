"""配置示例

演示如何在创建会话时配置 LLM。
"""

from compress_reme.reme_client import ReMeClient


def example_config_in_session():
    """在创建会话时指定 LLM 配置"""
    client = ReMeClient()
    
    # 方式 1: 使用 OpenAI
    llm_config_openai = {
        "model_name": "gpt-4o",
        "api_key": "your-openai-api-key",
        "base_url": "https://api.openai.com/v1",
        "temperature": 0.7,
        "max_tokens": 4000,
    }
    
    # 方式 2: 使用通义千问
    llm_config_qwen = {
        "model_name": "qwen-plus",
        "api_key": "your-dashscope-api-key",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "temperature": 0.7,
    }
    
    # 方式 3: 使用 DeepSeek
    llm_config_deepseek = {
        "model_name": "deepseek-chat",
        "api_key": "your-deepseek-api-key",
        "base_url": "https://api.deepseek.com/v1",
        "temperature": 0.7,
    }
    
    # 创建会话时传入配置
    client.create_session(
        session_id="my_session",
        llm_config=llm_config_openai,  # 选择一个配置
    )
    
    print("会话已创建，使用自定义 LLM 配置")


def example_config_from_env():
    """从环境变量读取配置"""
    import os
    
    # 设置环境变量
    os.environ["LLM_API_KEY"] = "your-api-key"
    os.environ["LLM_BASE_URL"] = "https://api.openai.com/v1"
    os.environ["LLM_MODEL_NAME"] = "gpt-4o"
    
    # 创建会话（将自动使用环境变量）
    client = ReMeClient()
    client.create_session("session_with_env")
    
    print("会话已创建，使用环境变量配置")


def example_different_models_per_session():
    """不同会话使用不同模型"""
    client = ReMeClient()
    
    # Session 1: 使用 GPT-4
    client.create_session(
        session_id="session_gpt4",
        llm_config={
            "model_name": "gpt-4o",
            "api_key": "your-openai-key",
            "base_url": "https://api.openai.com/v1",
        }
    )
    
    # Session 2: 使用通义千问
    client.create_session(
        session_id="session_qwen",
        llm_config={
            "model_name": "qwen-plus",
            "api_key": "your-qwen-key",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        }
    )
    
    # Session 3: 使用本地模型
    client.create_session(
        session_id="session_local",
        llm_config={
            "model_name": "llama3",
            "base_url": "http://localhost:11434/v1",  # Ollama
        }
    )
    
    print("创建了 3 个会话，每个使用不同的模型")


if __name__ == "__main__":
    print("配置示例")
    print("=" * 60)
    print("\n查看代码了解不同的配置方式：")
    print("1. example_config_in_session() - 在会话中配置")
    print("2. example_config_from_env() - 从环境变量配置")
    print("3. example_different_models_per_session() - 不同会话不同模型")
    print("\n实际使用时取消相应函数的注释")
