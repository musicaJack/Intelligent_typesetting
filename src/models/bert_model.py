"""
BERT模型核心类

提供BERT模型的加载、推理等功能。
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import torch
import torch.nn.functional as F
from loguru import logger
from transformers import (
    AutoModel,
    AutoTokenizer,
    BertForSequenceClassification,
    BertTokenizer,
    pipeline,
)

from ..config import Config


class BertModel:
    """BERT模型类"""
    
    def __init__(self, config: Config):
        """
        初始化BERT模型
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.model_config = config.model_config
        self.device = self._setup_device()
        
        # 初始化模型和分词器
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        
        # 加载模型
        self._load_model()
    
    def _setup_device(self) -> torch.device:
        """设置设备（CPU/GPU）"""
        device_config = self.model_config["bert"]["device"]
        
        if device_config == "auto":
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            device = torch.device(device_config)
        
        logger.info(f"使用设备: {device}")
        return device
    
    def _load_model(self):
        """加载BERT模型和分词器"""
        model_name = self.model_config["bert"]["model_name"]
        cache_dir = self.model_config["cache_dir"]
        
        logger.info(f"正在加载模型: {model_name}")
        
        try:
            # 加载分词器
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=cache_dir,
                use_fast=True,
            )
            
            # 加载模型
            self.model = AutoModel.from_pretrained(
                model_name,
                cache_dir=cache_dir,
            )
            
            # 移动到指定设备
            self.model.to(self.device)
            self.model.eval()
            
            logger.info("模型加载成功")
            
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise
    
    def encode_text(self, text: str, max_length: Optional[int] = None) -> Dict[str, torch.Tensor]:
        """
        编码文本
        
        Args:
            text: 输入文本
            max_length: 最大长度，默认使用配置中的值
            
        Returns:
            编码后的字典，包含input_ids, attention_mask等
        """
        if max_length is None:
            max_length = self.model_config["bert"]["max_length"]
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=max_length,
            return_tensors="pt",
        )
        
        # 移动到设备
        encoding = {k: v.to(self.device) for k, v in encoding.items()}
        
        return encoding
    
    def get_embeddings(self, text: str) -> torch.Tensor:
        """
        获取文本的BERT嵌入向量
        
        Args:
            text: 输入文本
            
        Returns:
            文本的嵌入向量
        """
        encoding = self.encode_text(text)
        
        with torch.no_grad():
            outputs = self.model(**encoding)
            # 使用[CLS]标记的输出作为句子嵌入
            embeddings = outputs.last_hidden_state[:, 0, :]
        
        return embeddings
    
    def get_sentence_embeddings(self, texts: List[str]) -> torch.Tensor:
        """
        批量获取句子嵌入向量
        
        Args:
            texts: 文本列表
            
        Returns:
            句子嵌入向量矩阵
        """
        batch_size = self.model_config["bert"]["batch_size"]
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            
            # 编码批次
            encoding = self.tokenizer(
                batch_texts,
                truncation=True,
                padding=True,
                max_length=self.model_config["bert"]["max_length"],
                return_tensors="pt",
            )
            
            # 移动到设备
            encoding = {k: v.to(self.device) for k, v in encoding.items()}
            
            with torch.no_grad():
                outputs = self.model(**encoding)
                embeddings = outputs.last_hidden_state[:, 0, :]
                all_embeddings.append(embeddings)
        
        return torch.cat(all_embeddings, dim=0)
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
            
        Returns:
            相似度分数（0-1之间）
        """
        # 获取嵌入向量
        emb1 = self.get_embeddings(text1)
        emb2 = self.get_embeddings(text2)
        
        # 计算余弦相似度
        similarity = F.cosine_similarity(emb1, emb2, dim=1)
        
        return similarity.item()
    
    def save_model(self, save_path: Optional[str] = None):
        """
        保存模型
        
        Args:
            save_path: 保存路径，默认使用配置中的路径
        """
        if save_path is None:
            save_path = self.model_config["save_path"]
        
        save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)
        
        # 保存模型和分词器
        self.model.save_pretrained(save_path)
        self.tokenizer.save_pretrained(save_path)
        
        logger.info(f"模型已保存到: {save_path}")
    
    def load_model(self, model_path: str):
        """
        从指定路径加载模型
        
        Args:
            model_path: 模型路径
        """
        model_path = Path(model_path)
        
        if not model_path.exists():
            raise FileNotFoundError(f"模型路径不存在: {model_path}")
        
        logger.info(f"正在从 {model_path} 加载模型")
        
        # 加载分词器和模型
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModel.from_pretrained(model_path)
        
        # 移动到设备
        self.model.to(self.device)
        self.model.eval()
        
        logger.info("模型加载成功")
    
    def create_pipeline(self, task: str, **kwargs) -> Any:
        """
        创建Hugging Face pipeline
        
        Args:
            task: 任务类型（如"text-classification", "token-classification"等）
            **kwargs: 其他参数
            
        Returns:
            pipeline对象
        """
        model_name = self.model_config["bert"]["model_name"]
        
        self.pipeline = pipeline(
            task,
            model=model_name,
            tokenizer=model_name,
            device=0 if self.device.type == "cuda" else -1,
            **kwargs
        )
        
        return self.pipeline 