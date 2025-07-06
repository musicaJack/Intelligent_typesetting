#!/usr/bin/env python3
"""
CKIP智能排版演示

演示如何使用CKIP Transformers引擎进行文本排版处理
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models.ckip_processor import CkipProcessor
from loguru import logger


def demo_basic_processing():
    """基础文本处理演示"""
    print("=" * 60)
    print("CKIP智能排版系统演示")
    print("=" * 60)
    
    # 示例文本
    sample_text = """弗农·德思札先生在一家名叫格朗宁的公司做主管，公司生产钻机。他高大魁梧，胖得几乎连脖子都没有，却蓄着一脸大胡子。德思礼太太是一个瘦削的金发女人。她的脖子几乎比正常人长一倍，这样每当她花许多时间隔着篱墙引颈而望、窥探左邻右舍时，她的长脖子可就派上了大用场。德思礼夫妇有一个小儿子，名叫达力。在他们看来，人世间没有比达力更好的孩子了。"""
    
    try:
        # 初始化CKIP处理器
        logger.info("正在初始化CKIP处理器...")
        processor = CkipProcessor(model_name="bert-base")
        
        # 处理文本
        logger.info("正在处理文本...")
        result = processor.process_text(sample_text)
        
        # 显示分词和词性标注结果
        print("\n📝 分词与词性标注结果:")
        print("-" * 40)
        for token in result["tokens"][:20]:  # 只显示前20个token
            print(f"{token['text']}({token['pos']})", end=" ")
        print("...")
        
        # 显示实体识别结果
        print("\n🏷️ 命名实体识别结果:")
        print("-" * 40)
        for entity in result["entities"]:
            print(f"• {entity['text']} ({entity['type']})")
        
        # 显示处理后的文本
        print("\n✨ 处理后的文本:")
        print("-" * 40)
        print(result["processed_text"])
        
        return processor
        
    except Exception as e:
        logger.error(f"处理失败: {e}")
        return None


def demo_layout_generation(processor):
    """排版生成演示"""
    print("\n" + "=" * 60)
    print("智能排版生成演示")
    print("=" * 60)
    
    # 示例文本
    sample_text = """弗农·德思札先生在一家名叫格朗宁的公司做主管，公司生产钻机。他高大魁梧，胖得几乎连脖子都没有，却蓄着一脸大胡子。德思礼太太是一个瘦削的金发女人。她的脖子几乎比正常人长一倍，这样每当她花许多时间隔着篱墙引颈而望、窥探左邻右舍时，她的长脖子可就派上了大用场。德思礼夫妇有一个小儿子，名叫达力。在他们看来，人世间没有比达力更好的孩子了。"""
    
    try:
        # 生成排版JSON
        output_file = "data/output/ckip_layout.json"
        logger.info("正在生成排版JSON...")
        
        layout_result = processor.create_layout_json(sample_text, output_file)
        
        # 显示排版信息
        print(f"\n📊 排版统计信息:")
        print("-" * 40)
        metadata = layout_result["metadata"]
        print(f"• 总页数: {metadata['total_pages']}")
        print(f"• 每行字符数: {metadata['chars_per_line']}")
        print(f"• 每页行数: {metadata['lines_per_page']}")
        print(f"• 总字符数: {metadata['total_chars']}")
        
        # 显示第一页内容
        if layout_result["pages"]:
            first_page = layout_result["pages"][0]
            print(f"\n📄 第一页内容 (共{len(first_page['lines'])}行):")
            print("-" * 40)
            for i, line in enumerate(first_page['lines'][:5], 1):  # 只显示前5行
                print(f"{i:2d}. {line['text']}")
            if len(first_page['lines']) > 5:
                print(f"    ... (还有{len(first_page['lines']) - 5}行)")
        
        # 显示实体信息
        if layout_result["pages"] and layout_result["pages"][0]["entities"]:
            print(f"\n🏷️ 第一页实体信息:")
            print("-" * 40)
            for entity in layout_result["pages"][0]["entities"]:
                print(f"• {entity['text']} ({entity['type']}) - 第{entity['line_idx'] + 1}行")
        
        print(f"\n✅ 排版JSON文件已保存: {output_file}")
        
    except Exception as e:
        logger.error(f"排版生成失败: {e}")


def demo_file_processing():
    """文件处理演示"""
    print("\n" + "=" * 60)
    print("文件处理演示")
    print("=" * 60)
    
    input_file = "files/input.txt"
    output_file = "data/output/ckip_file_layout.json"
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"❌ 输入文件不存在: {input_file}")
        print("请确保files/input.txt文件存在")
        return
    
    try:
        # 初始化处理器
        processor = CkipProcessor(model_name="bert-base")
        
        # 处理文件
        logger.info(f"正在处理文件: {input_file}")
        result = processor.process_file(input_file, output_file)
        
        print(f"\n✅ 文件处理完成!")
        print(f"📁 输入文件: {input_file}")
        print(f"📁 输出文件: {output_file}")
        print(f"📊 生成页数: {result['metadata']['total_pages']}")
        
    except Exception as e:
        logger.error(f"文件处理失败: {e}")


def main():
    """主函数"""
    print("🚀 启动CKIP智能排版系统演示")
    
    # 基础处理演示
    processor = demo_basic_processing()
    if processor is None:
        print("❌ 基础处理失败，退出演示")
        return
    
    # 排版生成演示
    demo_layout_generation(processor)
    
    # 文件处理演示
    demo_file_processing()
    
    print("\n" + "=" * 60)
    print("🎉 演示完成!")
    print("=" * 60)
    print("\n📋 使用说明:")
    print("1. 基础处理: 使用process_text()方法处理文本")
    print("2. 排版生成: 使用create_layout_json()生成排版JSON")
    print("3. 文件处理: 使用process_file()处理整个文件")
    print("\n📁 输出文件:")
    print("• data/output/ckip_layout.json - 排版JSON文件")
    print("• data/output/ckip_file_layout.json - 文件处理结果")


if __name__ == "__main__":
    main() 