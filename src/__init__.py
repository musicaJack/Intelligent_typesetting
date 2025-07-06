"""
智能排版应用 - 基于BERT模型的文本处理工具

这个包提供了基于BERT模型的智能排版功能，包括文本分类、命名实体识别、
文本相似度计算等功能。
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .config import Config
from .models import BertModel
from .utils import setup_logging

__all__ = ["Config", "BertModel", "setup_logging"] 