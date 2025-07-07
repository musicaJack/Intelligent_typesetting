#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试TXT格式的结构化标签生成（不依赖CKIP模型）
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models.ckip_processor import TokenInfo, EntityInfo, PageLayout

def test_txt_format_simple():
    """简单测试TXT格式的结构化标签"""
    
    # 创建模拟的页面数据
    pages = []
    
    # 第一页
    page1 = PageLayout(
        page_id=1,
        lines=[
            {"text": "哈利·波特与魔法石", "offset": 0, "length": 8},
            {"text": "", "offset": 8, "length": 0},
            {"text": "主要人物表", "offset": 8, "length": 5},
            {"text": "", "offset": 13, "length": 0},
            {"text": "哈利·波特：本书主人公", "offset": 13, "length": 12},
            {"text": "佩妮：哈利的姨妈", "offset": 25, "length": 8},
            {"text": "弗农·德思礼：哈利的姨父", "offset": 33, "length": 12},
            {"text": "达力：哈利的表哥", "offset": 45, "length": 9},
            {"text": "阿不思·邓布利多：校长", "offset": 54, "length": 12},
            {"text": "麦格教授：副校长", "offset": 66, "length": 9},
            {"text": "斯内普教授：魔药课教师", "offset": 75, "length": 12},
            {"text": "", "offset": 87, "length": 0}
        ],
        entities=[]
    )
    pages.append(page1)
    
    # 第二页
    page2 = PageLayout(
        page_id=2,
        lines=[
            {"text": "第1章 大难不死的男孩", "offset": 87, "length": 12},
            {"text": "", "offset": 99, "length": 0},
            {"text": "家住女贞路4号的德思礼夫妇", "offset": 99, "length": 14},
            {"text": "总是得意地说他们是非常规矩", "offset": 113, "length": 14},
            {"text": "的人家。拜托，拜托了。", "offset": 127, "length": 12},
            {"text": "他们从来跟神秘古怪的事", "offset": 139, "length": 12},
            {"text": "不沾边，因为他们根本不相信", "offset": 151, "length": 14},
            {"text": "那些邪门歪道。", "offset": 165, "length": 8},
            {"text": "", "offset": 173, "length": 0},
            {"text": "弗农·德思札先生在一家", "offset": 173, "length": 12},
            {"text": "名叫格朗宁的公司做主管", "offset": 185, "length": 12},
            {"text": "，公司生产钻机。", "offset": 197, "length": 9}
        ],
        entities=[]
    )
    pages.append(page2)
    
    # 模拟_generate_txt_content方法
    def generate_txt_content(pages):
        """生成适合小屏幕的纯文本内容，包含结构化标签供MCU检索"""
        lines = []
        
        for page in pages:
            # 添加页面开始标签（MCU可快速定位）
            if page.page_id > 1:
                lines.append("")
            lines.append(f"<PAGE_{page.page_id:03d}_START>")
            lines.append("")
            
            # 添加页面内容，每行都有行号标签
            for i, line_info in enumerate(page.lines, 1):
                # 添加行标签（MCU可快速定位到具体行）
                lines.append(f"<LINE_{page.page_id:03d}_{i:02d}> {line_info['text']}")
            
            # 添加页面结束标签
            lines.append(f"<PAGE_{page.page_id:03d}_END>")
            lines.append("")
        
        return "\n".join(lines)
    
    # 生成TXT内容
    txt_content = generate_txt_content(pages)
    
    # 保存测试文件
    with open("test_structured_simple.txt", "w", encoding="utf-8") as f:
        f.write(txt_content)
    
    print("✅ 测试文件已生成: test_structured_simple.txt")
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
    
    # 检查标签格式
    print("\n🔍 标签验证:")
    for i, start_tag in enumerate(page_starts):
        print(f"  页面 {i+1} 开始: {start_tag}")
    for i, end_tag in enumerate(page_ends):
        print(f"  页面 {i+1} 结束: {end_tag}")
    
    # 显示前几行内容
    print("\n📖 文件前20行内容:")
    for i, line in enumerate(lines[:20]):
        print(f"{i+1:2d}: {line}")
    
    return txt_content

if __name__ == "__main__":
    test_txt_format_simple() 