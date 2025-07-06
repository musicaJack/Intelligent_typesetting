#!/usr/bin/env python3
"""
CKIP处理器测试脚本

测试CKIP Transformers引擎的基本功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.models.ckip_processor import CkipProcessor
from loguru import logger


def test_ckip_processor():
    """测试CKIP处理器"""
    print("🧪 开始测试CKIP处理器...")
    
    # 测试文本
    test_text = "弗农·德思札先生在一家名叫格朗宁的公司做主管，公司生产钻机。"
    
    try:
        # 初始化处理器
        print("📦 正在初始化CKIP处理器...")
        processor = CkipProcessor(model_name="bert-base")
        
        # 测试文本处理
        print("🔍 正在处理测试文本...")
        result = processor.process_text(test_text)
        
        # 显示结果
        print("\n✅ 处理成功!")
        print(f"📝 原始文本: {test_text}")
        print(f"🔤 Token数量: {len(result['tokens'])}")
        print(f"🏷️ 实体数量: {len(result['entities'])}")
        
        # 显示分词结果
        print("\n📋 分词结果:")
        for i, token in enumerate(result['tokens'][:10], 1):
            print(f"  {i:2d}. {token['text']} ({token['pos']})")
        
        # 显示实体结果
        if result['entities']:
            print("\n🏷️ 实体识别结果:")
            for entity in result['entities']:
                print(f"  • {entity['text']} ({entity['type']})")
        
        # 测试排版生成
        print("\n📄 正在生成排版JSON...")
        output_file = "test_layout.json"
        layout_result = processor.create_layout_json(test_text, output_file)
        
        print(f"✅ 排版生成成功!")
        print(f"📊 页数: {layout_result['metadata']['total_pages']}")
        print(f"📏 每行字符数: {layout_result['metadata']['chars_per_line']}")
        print(f"📄 每页行数: {layout_result['metadata']['lines_per_page']}")
        
        if layout_result["pages"]:
            first_page = layout_result["pages"][0]
            print(f"\n📄 第一页内容:")
            for i, line in enumerate(first_page['lines'], 1):
                print(f"  {i}. {line['text']}")
        
        print(f"\n📁 输出文件: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        logger.error(f"测试失败: {e}")
        return False


def test_file_processing():
    """测试文件处理"""
    print("\n" + "="*50)
    print("📁 测试文件处理...")
    
    input_file = "files/input.txt"
    output_file = "test_file_layout.json"
    
    if not Path(input_file).exists():
        print(f"❌ 输入文件不存在: {input_file}")
        return False
    
    try:
        processor = CkipProcessor(model_name="bert-base")
        result = processor.process_file(input_file, output_file)
        
        print(f"✅ 文件处理成功!")
        print(f"📊 生成页数: {result['metadata']['total_pages']}")
        print(f"📝 总字符数: {result['metadata']['total_chars']}")
        print(f"📁 输出文件: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 文件处理失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 CKIP处理器测试")
    print("="*50)
    
    # 测试基本功能
    success1 = test_ckip_processor()
    
    # 测试文件处理
    success2 = test_file_processing()
    
    print("\n" + "="*50)
    if success1 and success2:
        print("🎉 所有测试通过!")
    else:
        print("❌ 部分测试失败")
    print("="*50)


if __name__ == "__main__":
    main() 