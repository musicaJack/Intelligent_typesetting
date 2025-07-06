"""
日志配置模块

提供统一的日志配置和管理。
"""

import sys
from pathlib import Path
from typing import Dict, Any

from loguru import logger


def setup_logging(config: Dict[str, Any]):
    """
    设置日志配置
    
    Args:
        config: 日志配置字典
    """
    # 移除默认的日志处理器
    logger.remove()
    
    # 获取配置参数
    level = config.get("level", "INFO")
    format_str = config.get("format", "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}")
    log_file = config.get("file", "./logs/app.log")
    rotation = config.get("rotation", "1 day")
    retention = config.get("retention", "30 days")
    
    # 创建日志目录
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 添加控制台处理器
    logger.add(
        sys.stdout,
        format=format_str,
        level=level,
        colorize=True,
    )
    
    # 添加文件处理器
    logger.add(
        log_file,
        format=format_str,
        level=level,
        rotation=rotation,
        retention=retention,
        encoding="utf-8",
    )
    
    logger.info("日志系统初始化完成")


def get_logger(name: str = None):
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        日志记录器
    """
    return logger.bind(name=name) if name else logger 