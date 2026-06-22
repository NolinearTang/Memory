"""
简化的配置管理 - 只负责加载YAML，返回字典kllm_config
"""
import os
import yaml
from pathlib import Path
from typing import Any, Dict


def _replace_env_vars(config: Any) -> Any:
    """递归替换配置中的环境变量"""
    if isinstance(config, dict):
        return {k: _replace_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [_replace_env_vars(item) for item in config]
    elif isinstance(config, str):
        # 处理 ${VAR} 和 ${VAR:default} 格式
        if config.startswith('${') and config.endswith('}'):
            var_expr = config[2:-1]
            if ':' in var_expr:
                var_name, default_value = var_expr.split(':', 1)
                return os.getenv(var_name, default_value)
            else:
                return os.getenv(var_expr, config)
        return config
    else:
        return config


def load_config(config_file: str = None) -> Dict[str, Any]:
    """
    加载配置文件，返回配置字典kllm_config
    
    Args:
        config_file: 配置文件路径，默认为config/config.yml
    
    Returns:
        kllm_config: 配置字典
    """
    if config_file is None:
        config_file = Path(__file__).parent / "config.yml"
    else:
        config_file = Path(config_file)
    
    if not config_file.exists():
        print(f"警告: 配置文件 {config_file} 不存在")
        return {}
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 替换环境变量
        config = _replace_env_vars(config)
        return config
    
    except yaml.YAMLError as e:
        print(f"警告: 配置文件解析失败: {e}")
        return {}
    except Exception as e:
        print(f"警告: 加载配置失败: {e}")
        return {}


# 全局配置字典
kllm_config: Dict[str, Any] = None


def get_config() -> Dict[str, Any]:
    """
    获取全局配置字典kllm_config
    
    Returns:
        kllm_config: 配置字典
    """
    global kllm_config
    
    if kllm_config is None:
        kllm_config = load_config()
    
    return kllm_config


def reload_config():
    """重新加载配置"""
    global kllm_config
    kllm_config = load_config()


if __name__ == '__main__':
    # 测试配置加载
    config = get_config()
    
    print("=== 配置加载测试 ===")
    print(f"配置字典: {config}")
    
    # 测试获取model_hub中的模型
    if 'model_hub' in config:
        print(f"\n可用模型: {list(config['model_hub'].keys())}")
        
        selected_model = config.get('llm', {}).get('selected_model', 'gpt4')
        print(f"选中模型: {selected_model}")
        
        model_config = config['model_hub'].get(selected_model, {})
        print(f"模型配置: {model_config}")
