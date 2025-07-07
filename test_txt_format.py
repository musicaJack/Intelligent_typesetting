#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试TXT格式的结构化标签生成
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models.ckip_processor import CkipProcessor, TokenInfo, EntityInfo

def test_txt_format():
    """测试TXT格式的结构化标签"""
    
    # 初始化处理器
    processor = CkipProcessor(model_name="bert-base")
    processor.chars_per_line = 16
    processor.lines_per_page = 12
    
    # 测试文本
    test_text = """哈利·波特与魔法石

主要人物表

哈利·波特：本书主人公，霍格沃茨魔法学校一年级学生
佩妮：哈利的姨妈
弗农·德思礼：哈利的姨父
达力：哈利的表哥，德思礼夫妇的儿子
阿不思·邓布利多：霍格沃茨魔法学校校长
麦格教授：霍格沃茨魔法学校副校长
斯内普教授：霍格沃茨魔法学校魔药课教师

第1章 大难不死的男孩

家住女贞路4号的德思礼夫妇总是得意地说他们是非常规矩的人家。拜托，拜托了。他们从来跟神秘古怪的事不沾边，因为他们根本不相信那些邪门歪道。弗农·德思札先生在一家名叫格朗宁的公司做主管，公司生产钻机。"""
    
    # 处理文本
    result = processor.process_text(test_text)
    tokens = [TokenInfo(**token_dict) for token_dict in result["tokens"]]
    entities = [EntityInfo(**entity_dict) for entity_dict in result["entities"]]
    
    # 生成页面布局
    pages = processor._generate_pages(tokens, entities)
    
    # 生成TXT内容
    txt_content = processor._generate_txt_content(pages)
    
    # 保存测试文件
    with open("test_structured.txt", "w", encoding="utf-8") as f:
        f.write(txt_content)
    
    print("✅ 测试文件已生成: test_structured.txt")
    print(f"📄 总页数: {len(pages)}")
    print(f"📝 总行数: {sum(len(page.lines) for page in pages)}")
    
    # 验证标签格式
    lines = txt_content.split('\n')
    page_starts = [line for line in lines if line.startswith('<PAGE_') and line.endswith('_START>')]
    page_ends = [line for line in lines if line.startswith('<PAGE_') and line.endswith('_END>')]
    line_tags = [line for line in lines if line.startswith('<LINE_')]
    
    print(f"🏷️ 页面开始标签: {len(page_starts)}")
    print(f"🏷️ 页面结束标签: {len(page_ends)}")
    print(f"🏷️ 行标签: {len(line_tags)}")
    
    # 检查第一页是否有START标签
    if any('PAGE_001_START' in line for line in lines):
        print("✅ 第一页包含PAGE_001_START标签")
    else:
        print("❌ 第一页缺少PAGE_001_START标签")
    
    # 显示前几行内容
    print("\n📖 文件前20行内容:")
    for i, line in enumerate(lines[:20]):
        print(f"{i+1:2d}: {line}")
    
    return txt_content

if __name__ == "__main__":
    test_txt_format() 