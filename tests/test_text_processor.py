"""
文本处理模块测试

测试文本预处理和后处理功能。
"""

import pytest
from src.models.text_processor import TextProcessor


class TestTextProcessor:
    """文本处理器测试"""
    
    def setup_method(self):
        """设置测试方法"""
        self.processor = TextProcessor()
    
    def test_clean_text(self):
        """测试文本清理"""
        # 测试基本清理
        text = "  这是一个  测试文本  \n\n  包含多余的空格  "
        cleaned = self.processor.clean_text(text)
        assert cleaned == "这是一个 测试文本 包含多余的空格"
        
        # 测试特殊字符清理
        text = "测试文本@#$%^&*()包含特殊字符"
        cleaned = self.processor.clean_text(text)
        assert "特殊字符" in cleaned
        assert "@#$%^&*()" not in cleaned
    
    def test_normalize_text(self):
        """测试文本标准化"""
        # 测试全角转半角
        text = "这是一个全角文本，包含全角标点符号！？"
        normalized = self.processor.normalize_text(text)
        assert "，" not in normalized
        assert "！" not in normalized
        assert "？" not in normalized
        
        # 测试标点符号统一
        text = "中文标点：，。！？；英文标点:,.!?;"
        normalized = self.processor.normalize_text(text)
        assert "：" not in normalized
        assert "，" not in normalized
        assert "。" not in normalized
    
    def test_split_sentences(self):
        """测试句子分割"""
        text = "这是第一个句子。这是第二个句子！这是第三个句子？"
        sentences = self.processor.split_sentences(text)
        assert len(sentences) == 3
        assert "第一个句子" in sentences[0]
        assert "第二个句子" in sentences[1]
        assert "第三个句子" in sentences[2]
        
        # 测试空文本
        sentences = self.processor.split_sentences("")
        assert sentences == []
    
    def test_split_paragraphs(self):
        """测试段落分割"""
        text = "第一段内容。\n\n第二段内容。\n\n第三段内容。"
        paragraphs = self.processor.split_paragraphs(text)
        assert len(paragraphs) == 3
        assert "第一段内容" in paragraphs[0]
        assert "第二段内容" in paragraphs[1]
        assert "第三段内容" in paragraphs[2]
    
    def test_extract_keywords(self):
        """测试关键词提取"""
        text = "这是一个关于人工智能和机器学习的测试文本。人工智能技术正在快速发展。"
        keywords = self.processor.extract_keywords(text, top_k=5)
        
        # 验证关键词提取结果
        assert len(keywords) <= 5
        assert all(isinstance(k, str) for k in keywords)
        
        # 测试空文本
        keywords = self.processor.extract_keywords("", top_k=10)
        assert keywords == []
    
    def test_format_text(self):
        """测试文本格式化"""
        text = "这是一个很长的句子，需要被格式化处理。这是另一个句子。这是第三个句子。"
        formatted = self.processor.format_text(text, max_line_length=20)
        
        # 验证格式化结果
        lines = formatted.split('\n')
        for line in lines:
            assert len(line) <= 20
        
        # 测试空文本
        formatted = self.processor.format_text("", max_line_length=80)
        assert formatted == ""
    
    def test_full_to_half(self):
        """测试全角转半角"""
        text = "１２３ＡＢＣａｂｃ"
        result = self.processor._full_to_half(text)
        assert result == "123ABCabc"
        
        # 测试全角空格
        text = "全角　空格"
        result = self.processor._full_to_half(text)
        assert "　" not in result
    
    def test_normalize_punctuation(self):
        """测试标点符号标准化"""
        text = "中文标点：，。！？；英文标点:,.!?;"
        result = self.processor._normalize_punctuation(text)
        
        # 验证中文标点被转换为英文标点
        assert "：" not in result
        assert "，" not in result
        assert "。" not in result
        assert "！" not in result
        assert "？" not in result
        assert "；" not in result 