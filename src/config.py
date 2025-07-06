"""
配置管理模块

负责加载和管理应用的配置参数，包括模型配置、数据处理配置等。
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv


class Config:
    """配置管理类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，默认为 config/config.yaml
        """
        # 加载环境变量
        load_dotenv()
        
        # 设置默认配置文件路径
        if config_path is None:
            config_path = "config/config.yaml"
        
        self.config_path = Path(config_path)
        self._config = self._load_config()
        
        # 创建必要的目录
        self._create_directories()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 处理环境变量覆盖
        config = self._process_env_overrides(config)
        
        return config
    
    def _process_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """处理环境变量覆盖配置"""
        # 模型设备配置
        if os.getenv("MODEL_DEVICE"):
            config["model"]["bert"]["device"] = os.getenv("MODEL_DEVICE")
        
        # 调试模式
        debug_env = os.getenv("DEBUG")
        if debug_env:
            config["app"]["debug"] = debug_env.lower() == "true"
        
        # 日志级别
        if os.getenv("LOG_LEVEL"):
            config["logging"]["level"] = os.getenv("LOG_LEVEL")
        
        return config
    
    def _create_directories(self):
        """创建必要的目录"""
        directories = [
            self.get("data.input_dir"),
            self.get("data.output_dir"),
            self.get("model.cache_dir"),
            Path(self.get("logging.file")).parent,
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """
        设置配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键
            value: 配置值
        """
        keys = key.split('.')
        config = self._config
        
        # 导航到父级
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
    
    def save(self, path: Optional[str] = None):
        """
        保存配置到文件
        
        Args:
            path: 保存路径，默认为原始配置文件路径
        """
        save_path = Path(path) if path else self.config_path
        
        with open(save_path, 'w', encoding='utf-8') as f:
            yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)
    
    @property
    def model_config(self) -> Dict[str, Any]:
        """获取模型配置"""
        return self.get("model", {})
    
    @property
    def data_config(self) -> Dict[str, Any]:
        """获取数据处理配置"""
        return self.get("data", {})
    
    @property
    def training_config(self) -> Dict[str, Any]:
        """获取训练配置"""
        return self.get("training", {})
    
    @property
    def inference_config(self) -> Dict[str, Any]:
        """获取推理配置"""
        return self.get("inference", {})
    
    @property
    def logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.get("logging", {})
    
    @property
    def api_config(self) -> Dict[str, Any]:
        """获取API配置"""
        return self.get("api", {}) 