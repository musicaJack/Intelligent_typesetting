"""
文件工具模块

提供文件读写、格式转换等功能。
"""

import json
import csv
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from loguru import logger


class FileUtils:
    """文件工具类"""
    
    def __init__(self, encoding: str = "utf-8"):
        """
        初始化文件工具
        
        Args:
            encoding: 文件编码
        """
        self.encoding = encoding
    
    def read_text(self, file_path: Union[str, Path]) -> str:
        """
        读取文本文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        try:
            with open(file_path, 'r', encoding=self.encoding) as f:
                content = f.read()
            logger.debug(f"成功读取文件: {file_path}")
            return content
        except Exception as e:
            logger.error(f"读取文件失败 {file_path}: {e}")
            raise
    
    def write_text(self, file_path: Union[str, Path], content: str):
        """
        写入文本文件
        
        Args:
            file_path: 文件路径
            content: 文件内容
        """
        file_path = Path(file_path)
        
        # 创建目录
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, 'w', encoding=self.encoding) as f:
                f.write(content)
            logger.debug(f"成功写入文件: {file_path}")
        except Exception as e:
            logger.error(f"写入文件失败 {file_path}: {e}")
            raise
    
    def read_json(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        读取JSON文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            JSON数据
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        try:
            with open(file_path, 'r', encoding=self.encoding) as f:
                data = json.load(f)
            logger.debug(f"成功读取JSON文件: {file_path}")
            return data
        except Exception as e:
            logger.error(f"读取JSON文件失败 {file_path}: {e}")
            raise
    
    def write_json(self, file_path: Union[str, Path], data: Dict[str, Any], indent: int = 2):
        """
        写入JSON文件
        
        Args:
            file_path: 文件路径
            data: JSON数据
            indent: 缩进空格数
        """
        file_path = Path(file_path)
        
        # 创建目录
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, 'w', encoding=self.encoding) as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
            logger.debug(f"成功写入JSON文件: {file_path}")
        except Exception as e:
            logger.error(f"写入JSON文件失败 {file_path}: {e}")
            raise
    
    def read_csv(self, file_path: Union[str, Path]) -> List[Dict[str, str]]:
        """
        读取CSV文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            CSV数据列表
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        try:
            data = []
            with open(file_path, 'r', encoding=self.encoding, newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
            logger.debug(f"成功读取CSV文件: {file_path}")
            return data
        except Exception as e:
            logger.error(f"读取CSV文件失败 {file_path}: {e}")
            raise
    
    def write_csv(self, file_path: Union[str, Path], data: List[Dict[str, str]], fieldnames: Optional[List[str]] = None):
        """
        写入CSV文件
        
        Args:
            file_path: 文件路径
            data: CSV数据列表
            fieldnames: 字段名列表
        """
        file_path = Path(file_path)
        
        # 创建目录
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, 'w', encoding=self.encoding, newline='') as f:
                if not fieldnames and data:
                    fieldnames = list(data[0].keys())
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            logger.debug(f"成功写入CSV文件: {file_path}")
        except Exception as e:
            logger.error(f"写入CSV文件失败 {file_path}: {e}")
            raise
    
    def get_file_extension(self, file_path: Union[str, Path]) -> str:
        """
        获取文件扩展名
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件扩展名（不含点）
        """
        return Path(file_path).suffix.lstrip('.')
    
    def is_supported_format(self, file_path: Union[str, Path], supported_formats: List[str]) -> bool:
        """
        检查文件格式是否支持
        
        Args:
            file_path: 文件路径
            supported_formats: 支持的文件格式列表
            
        Returns:
            是否支持
        """
        extension = self.get_file_extension(file_path)
        return extension.lower() in [fmt.lower() for fmt in supported_formats]
    
    def list_files(self, directory: Union[str, Path], pattern: str = "*") -> List[Path]:
        """
        列出目录中的文件
        
        Args:
            directory: 目录路径
            pattern: 文件匹配模式
            
        Returns:
            文件路径列表
        """
        directory = Path(directory)
        
        if not directory.exists():
            logger.warning(f"目录不存在: {directory}")
            return []
        
        files = list(directory.glob(pattern))
        logger.debug(f"在目录 {directory} 中找到 {len(files)} 个文件")
        return files 