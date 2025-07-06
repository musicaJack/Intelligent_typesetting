"""
文本处理模块

提供文本预处理、后处理等功能。
"""

import re
from typing import List, Optional, Union

from loguru import logger


class TextProcessor:
    """文本处理器"""
    
    def __init__(self):
        """初始化文本处理器"""
        # 中文标点符号
        self.chinese_punctuation = "，。！？；：""''（）【】《》、"
        # 英文标点符号
        self.english_punctuation = ",.!?;:\"'()[]<>/"
    
    def clean_text(self, text: str) -> str:
        """
        清理文本
        
        Args:
            text: 输入文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        
        # 去除多余的空白字符
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 去除特殊字符（保留中文、英文、数字、标点）
        text = re.sub(r'[^\u4e00-\u9fff\w\s.,!?;:()\[\]<>""''（）【】《》、，。！？；：]', '', text)
        
        return text
    
    def normalize_text(self, text: str) -> str:
        """
        标准化文本
        
        Args:
            text: 输入文本
            
        Returns:
            标准化后的文本
        """
        if not text:
            return ""
        
        # 全角转半角
        text = self._full_to_half(text)
        
        # 统一标点符号
        text = self._normalize_punctuation(text)
        
        # 清理文本
        text = self.clean_text(text)
        
        return text
    
    def _full_to_half(self, text: str) -> str:
        """全角转半角"""
        result = ""
        for char in text:
            code = ord(char)
            if code == 0x3000:  # 全角空格
                result += ' '
            elif 0xFF01 <= code <= 0xFF5E:  # 全角字符
                result += chr(code - 0xFEE0)
            else:
                result += char
        return result
    
    def _normalize_punctuation(self, text: str) -> str:
        """标准化标点符号"""
        # 中文标点转英文标点
        punctuation_map = {
            '，': ',', '。': '.', '！': '!', '？': '?',
            '；': ';', '：': ':', '"': '"', '"': '"',
            ''': "'", ''': "'", '（': '(', '）': ')',
            '【': '[', '】': ']', '《': '<', '》': '>',
            '、': ','
        }
        
        for chinese, english in punctuation_map.items():
            text = text.replace(chinese, english)
        
        return text
    
    def split_sentences(self, text: str) -> List[str]:
        """
        分割句子
        
        Args:
            text: 输入文本
            
        Returns:
            句子列表
        """
        if not text:
            return []
        
        # 使用正则表达式分割句子
        sentences = re.split(r'[.!?。！？]+', text)
        
        # 过滤空句子并清理
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def split_paragraphs(self, text: str) -> List[str]:
        """
        分割段落
        
        Args:
            text: 输入文本
            
        Returns:
            段落列表
        """
        if not text:
            return []
        
        # 按双换行符分割段落
        paragraphs = re.split(r'\n\s*\n', text)
        
        # 过滤空段落并清理
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        return paragraphs
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """
        提取关键词（简单实现）
        
        Args:
            text: 输入文本
            top_k: 返回前k个关键词
            
        Returns:
            关键词列表
        """
        if not text:
            return []
        
        # 简单的关键词提取：按词频统计
        words = re.findall(r'\w+', text.lower())
        
        # 过滤停用词（这里可以扩展）
        stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
        words = [w for w in words if w not in stop_words and len(w) > 1]
        
        # 统计词频
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 按频率排序
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, freq in sorted_words[:top_k]]
    
    def format_text(self, text: str, max_line_length: int = 80) -> str:
        """
        格式化文本
        
        Args:
            text: 输入文本
            max_line_length: 最大行长度
            
        Returns:
            格式化后的文本
        """
        if not text:
            return ""
        
        # 分割成句子
        sentences = self.split_sentences(text)
        
        formatted_lines = []
        current_line = ""
        
        for sentence in sentences:
            # 如果当前行加上新句子不超过最大长度，就添加到当前行
            if len(current_line) + len(sentence) <= max_line_length:
                current_line += sentence + ". "
            else:
                # 否则开始新行
                if current_line:
                    formatted_lines.append(current_line.strip())
                current_line = sentence + ". "
        
        # 添加最后一行
        if current_line:
            formatted_lines.append(current_line.strip())
        
        return "\n".join(formatted_lines) 