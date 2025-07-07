"""
CKIP Transformers文本处理模块

提供基于CKIP Transformers引擎的文本预处理功能：
- 中文分词
- 词性标注  
- 命名实体识别
- 智能排版预处理
"""

import json
import re
import torch
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path

from loguru import logger
from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger, CkipNerChunker


@dataclass
class TokenInfo:
    """词元信息"""
    text: str
    pos: str
    start: int
    end: int
    is_entity: bool = False
    entity_type: Optional[str] = None


@dataclass
class EntityInfo:
    """实体信息"""
    text: str
    type: str
    start: int
    end: int


@dataclass
class PageLayout:
    """页面布局信息"""
    page_id: int
    lines: List[Dict[str, Any]]
    entities: List[Dict[str, Any]]
    total_chars: int = 0


class CkipProcessor:
    """CKIP文本处理器"""
    
    def __init__(self, model_name: str = "bert-base", device: str = "auto"):
        """
        初始化CKIP处理器
        
        Args:
            model_name: 使用的模型名称，默认使用bert-base
            device: 设备类型，"auto", "cpu", "cuda", "cuda:0"等
        """
        self.model_name = model_name
        self.device = self._get_device(device)
        self.ws_driver = None
        self.pos_driver = None
        self.ner_driver = None
        
        # 排版配置
        self.chars_per_line = 35  # 每行35个中文字符
        self.lines_per_page = 18  # 每页18行
        
        # 标点符号映射
        self.punctuation_map = {
            '，': ',', '。': '.', '！': '!', '？': '?',
            '；': ';', '：': ':', '"': '"', '"': '"',
            ''': "'", ''': "'", '（': '(', '）': ')',
            '【': '[', '】': ']', '《': '<', '》': '>',
            '、': ',', '…': '...'
        }
        
        # 不可分割的标点符号（不能出现在行首）
        self.no_break_punctuation = {',', '，', '.', '。', '!', '！', '?', '？', ';', '；', ':', '：'}
        
        # 初始化模型
        self._load_models()
    
    def _get_device(self, device: str) -> str:
        """获取设备配置"""
        if device == "auto":
            if torch.cuda.is_available():
                # 检测GPU数量和显存
                gpu_count = torch.cuda.device_count()
                logger.info(f"检测到 {gpu_count} 个GPU设备")
                
                for i in range(gpu_count):
                    gpu_name = torch.cuda.get_device_name(i)
                    gpu_memory = torch.cuda.get_device_properties(i).total_memory / (1024**3)
                    logger.info(f"GPU {i}: {gpu_name}, 显存: {gpu_memory:.1f}GB")
                
                # 使用第一个GPU
                device = "cuda:0"
                logger.info(f"自动选择设备: {device}")
            else:
                device = "cpu"
                logger.info("未检测到GPU，使用CPU")
        else:
            logger.info(f"使用指定设备: {device}")
        
        return device
    
    def _load_models(self):
        """加载CKIP模型"""
        try:
            logger.info(f"正在加载CKIP模型: {self.model_name}")
            logger.info(f"使用设备: {self.device}")
            
            # 设置设备
            device_kwargs = {"device": self.device} if self.device != "cpu" else {}
            
            self.ws_driver = CkipWordSegmenter(model=self.model_name, **device_kwargs)
            self.pos_driver = CkipPosTagger(model=self.model_name, **device_kwargs)
            self.ner_driver = CkipNerChunker(model=self.model_name, **device_kwargs)
            
            logger.info("CKIP模型加载成功")
            
            # 显示GPU使用情况
            if self.device.startswith("cuda"):
                gpu_memory_allocated = torch.cuda.memory_allocated(0) / (1024**3)
                gpu_memory_reserved = torch.cuda.memory_reserved(0) / (1024**3)
                logger.info(f"GPU显存使用: {gpu_memory_allocated:.2f}GB (已分配) / {gpu_memory_reserved:.2f}GB (已保留)")
            
        except Exception as e:
            logger.error(f"CKIP模型加载失败: {e}")
            # 确保模型加载失败时设置为None
            self.ws_driver = None
            self.pos_driver = None
            self.ner_driver = None
            raise
    
    def process_text(self, text: str) -> Dict[str, Any]:
        """
        处理文本，返回分词、词性标注和实体识别结果
        
        Args:
            text: 输入文本
            
        Returns:
            处理结果字典
        """
        if not text.strip():
            return {"tokens": [], "entities": [], "processed_text": ""}
        
        try:
            # 检查模型是否已加载
            if not all([self.ws_driver, self.pos_driver, self.ner_driver]):
                self._load_models()
            
            # 分词
            ws_result = self.ws_driver([text])
            
            # 词性标注
            pos_result = self.pos_driver(ws_result)
            
            # 实体识别
            ner_result = self.ner_driver([text])
            
            # 构建token信息
            tokens = self._build_tokens(text, ws_result[0], pos_result[0], ner_result[0])
            
            # 提取实体信息
            entities = self._extract_entities(ner_result[0])
            
            # 生成处理后的文本
            processed_text = self._generate_processed_text(tokens)
            
            return {
                "tokens": [asdict(token) for token in tokens],
                "entities": [asdict(entity) for entity in entities],
                "processed_text": processed_text,
                "original_text": text
            }
            
        except Exception as e:
            logger.error(f"文本处理失败: {e}")
            raise
    
    def _build_tokens(self, text: str, ws: List[str], pos: List[str], ner: List) -> List[TokenInfo]:
        """构建token信息列表"""
        tokens = []
        current_pos = 0
        
        # 创建实体位置映射
        entity_map = {}
        for entity in ner:
            entity_map[(entity.idx[0], entity.idx[1])] = entity.ner
        
        for word, pos_tag in zip(ws, pos):
            # 查找词在原文中的位置
            start = text.find(word, current_pos)
            if start == -1:
                start = current_pos
            end = start + len(word)
            
            # 检查是否为实体
            is_entity = (start, end) in entity_map
            entity_type = entity_map.get((start, end))
            
            token = TokenInfo(
                text=word,
                pos=pos_tag,
                start=start,
                end=end,
                is_entity=is_entity,
                entity_type=entity_type
            )
            tokens.append(token)
            current_pos = end
        
        return tokens
    
    def _extract_entities(self, ner_result: List) -> List[EntityInfo]:
        """提取实体信息"""
        entities = []
        for entity in ner_result:
            entity_info = EntityInfo(
                text=entity.word,
                type=entity.ner,
                start=entity.idx[0],
                end=entity.idx[1]
            )
            entities.append(entity_info)
        return entities
    
    def _generate_processed_text(self, tokens: List[TokenInfo]) -> str:
        """生成处理后的文本"""
        # 按位置排序
        sorted_tokens = sorted(tokens, key=lambda x: x.start)
        
        # 构建文本，保持原始格式
        processed_parts = []
        for token in sorted_tokens:
            # 标准化标点符号
            text = token.text
            for chinese, english in self.punctuation_map.items():
                text = text.replace(chinese, english)
            processed_parts.append(text)
        
        return "".join(processed_parts)
    
    def create_layout_json(self, text: str, output_path: str) -> Dict[str, Any]:
        """
        创建排版JSON文件
        
        Args:
            text: 输入文本
            output_path: 输出文件路径
            
        Returns:
            排版结果字典
        """
        # 处理文本
        result = self.process_text(text)
        tokens = [TokenInfo(**token_dict) for token_dict in result["tokens"]]
        entities = [EntityInfo(**entity_dict) for entity_dict in result["entities"]]
        
        # 生成页面布局
        pages = self._generate_pages(tokens, entities)
        
        # 构建JSON结构
        layout_data = {
            "metadata": {
                "title": "智能排版文本",
                "total_pages": len(pages),
                "chars_per_line": self.chars_per_line,
                "lines_per_page": self.lines_per_page,
                "total_chars": sum(page.total_chars for page in pages)
            },
            "pages": [asdict(page) for page in pages]
        }
        
        # 保存JSON文件
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(layout_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"排版JSON文件已保存: {output_file}")
        return layout_data
    
    def _generate_pages(self, tokens: List[TokenInfo], entities: List[EntityInfo]) -> List[PageLayout]:
        """生成页面布局"""
        pages = []
        current_page = PageLayout(page_id=1, lines=[], entities=[])
        current_line = ""
        current_line_tokens = []
        line_offset = 0
        
        # 创建实体位置映射
        entity_positions = {}
        for entity in entities:
            for i in range(entity.start, entity.end):
                entity_positions[i] = entity
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            # 检查是否需要换行
            if self._should_break_line(current_line, token, current_line_tokens):
                # 完成当前行
                if current_line:
                    line_info = {
                        "text": current_line,
                        "offset": line_offset,
                        "length": len(current_line),
                        "tokens": [asdict(t) for t in current_line_tokens]
                    }
                    current_page.lines.append(line_info)
                    current_page.total_chars += len(current_line)
                    line_offset += len(current_line)
                
                # 检查是否需要换页
                if len(current_page.lines) >= self.lines_per_page:
                    pages.append(current_page)
                    current_page = PageLayout(
                        page_id=len(pages) + 1,
                        lines=[],
                        entities=[]
                    )
                
                # 开始新行
                current_line = ""
                current_line_tokens = []
            
            # 添加token到当前行
            current_line += token.text
            current_line_tokens.append(token)
            
            i += 1
        
        # 处理最后一行
        if current_line:
            line_info = {
                "text": current_line,
                "offset": line_offset,
                "length": len(current_line),
                "tokens": [asdict(t) for t in current_line_tokens]
            }
            current_page.lines.append(line_info)
            current_page.total_chars += len(current_line)
        
        # 添加最后一页
        if current_page.lines:
            pages.append(current_page)
        
        # 添加实体信息到页面
        self._add_entities_to_pages(pages, entities)
        
        return pages
    
    def _should_break_line(self, current_line: str, token: TokenInfo, current_tokens: List[TokenInfo]) -> bool:
        """判断是否需要换行"""
        # 如果当前行加上新token超过字符限制
        if len(current_line) + len(token.text) > self.chars_per_line:
            return True
        
        # 如果当前token是标点符号且不能出现在行首
        if token.text in self.no_break_punctuation and len(current_line) == 0:
            return False
        
        # 如果下一个token是标点符号，尝试不换行
        return False
    
    def _add_entities_to_pages(self, pages: List[PageLayout], entities: List[EntityInfo]):
        """将实体信息添加到页面中"""
        for page in pages:
            page_entities = []
            for entity in entities:
                # 检查实体是否在当前页面中
                for line in page.lines:
                    line_start = line["offset"]
                    line_end = line_start + line["length"]
                    
                    if (entity.start >= line_start and entity.start < line_end) or \
                       (entity.end > line_start and entity.end <= line_end):
                        entity_info = {
                            "text": entity.text,
                            "type": entity.type,
                            "start": entity.start - line_start,
                            "end": entity.end - line_start,
                            "line_idx": page.lines.index(line)
                        }
                        page_entities.append(entity_info)
                        break
            
            page.entities = page_entities
    
    def process_file(self, input_file: str, output_file: str) -> Dict[str, Any]:
        """
        处理文件并生成排版JSON
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            
        Returns:
            处理结果
        """
        try:
            # 读取输入文件
            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            logger.info(f"读取文件: {input_file}, 字符数: {len(text)}")
            
            # 生成排版JSON
            result = self.create_layout_json(text, output_file)
            
            logger.info(f"处理完成，生成 {result['metadata']['total_pages']} 页")
            return result
            
        except Exception as e:
            logger.error(f"文件处理失败: {e}")
            raise
    
    def process_file_txt(self, input_file: str, output_file: str) -> Dict[str, Any]:
        """
        处理文件并生成适合小屏幕的纯文本排版
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            
        Returns:
            处理结果
        """
        try:
            # 读取输入文件
            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            logger.info(f"读取文件: {input_file}, 字符数: {len(text)}")
            
            # 处理文本
            result = self.process_text(text)
            tokens = [TokenInfo(**token_dict) for token_dict in result["tokens"]]
            entities = [EntityInfo(**entity_dict) for entity_dict in result["entities"]]
            
            # 生成页面布局
            pages = self._generate_pages(tokens, entities)
            
            # 生成纯文本输出
            txt_content = self._generate_txt_content(pages)
            
            # 保存TXT文件
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(txt_content)
            
            # 构建返回结果
            layout_data = {
                "metadata": {
                    "title": "智能排版文本",
                    "total_pages": len(pages),
                    "chars_per_line": self.chars_per_line,
                    "lines_per_page": self.lines_per_page,
                    "total_chars": sum(page.total_chars for page in pages)
                },
                "pages": [asdict(page) for page in pages]
            }
            
            logger.info(f"TXT文件已保存: {output_path}")
            return layout_data
            
        except Exception as e:
            logger.error(f"文件处理失败: {e}")
            raise
    
    def _generate_txt_content(self, pages: List[PageLayout]) -> str:
        """生成适合小屏幕的纯文本内容"""
        lines = []
        
        for page in pages:
            # 添加页面分隔符
            if page.page_id > 1:
                lines.append("")
                lines.append("=" * self.chars_per_line)
                lines.append(f"第 {page.page_id} 页")
                lines.append("=" * self.chars_per_line)
                lines.append("")
            
            # 添加页面内容
            for line_info in page.lines:
                lines.append(line_info["text"])
            
            # 页面结束
            lines.append("") 