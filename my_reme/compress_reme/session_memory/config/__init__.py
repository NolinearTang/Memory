"""
配置管理模块 - 简化版
"""
from config.config import get_config, reload_config, kllm_config

__all__ = ['get_config', 'reload_config', 'kllm_config']
