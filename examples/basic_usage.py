"""
基本使用示例

演示如何使用智能排版应用的基本功能。
"""

from src.config import Config
from src.models import BertModel, TextProcessor
from src.utils import setup_logging


def main():
    """主函数 - 演示基本功能"""
    
    # 1. 加载配置
    print("正在加载配置...")
    config = Config()
    setup_logging(config.logging_config)
    
    # 2. 初始化组件
    print("正在初始化模型...")
    bert_model = BertModel(config)
    text_processor = TextProcessor()
    
    # 3. 示例文本
    sample_texts = [
        "这是一个测试文本，包含一些标点符号！？",
        "这是另一个测试文本，用于演示功能。",
        "人工智能技术正在快速发展，BERT模型在自然语言处理中发挥重要作用。"
    ]
    
    # 4. 文本处理示例
    print("\n=== 文本处理示例 ===")
    for i, text in enumerate(sample_texts, 1):
        print(f"\n原始文本 {i}: {text}")
        
        # 清理和标准化
        cleaned_text = text_processor.clean_text(text)
        normalized_text = text_processor.normalize_text(text)
        
        print(f"清理后: {cleaned_text}")
        print(f"标准化后: {normalized_text}")
        
        # 分割句子
        sentences = text_processor.split_sentences(text)
        print(f"句子数量: {len(sentences)}")
        
        # 提取关键词
        keywords = text_processor.extract_keywords(text, top_k=5)
        print(f"关键词: {', '.join(keywords)}")
    
    # 5. 文本相似度计算示例
    print("\n=== 文本相似度计算示例 ===")
    text1 = "人工智能技术正在快速发展"
    text2 = "AI技术发展迅速"
    text3 = "今天天气很好"
    
    similarity_12 = bert_model.calculate_similarity(text1, text2)
    similarity_13 = bert_model.calculate_similarity(text1, text3)
    
    print(f"文本1: {text1}")
    print(f"文本2: {text2}")
    print(f"文本3: {text3}")
    print(f"文本1与文本2的相似度: {similarity_12:.4f}")
    print(f"文本1与文本3的相似度: {similarity_13:.4f}")
    
    # 6. 文本格式化示例
    print("\n=== 文本格式化示例 ===")
    long_text = "这是一个很长的文本，需要被格式化处理。它包含多个句子，每个句子都有不同的长度。格式化后的文本应该更容易阅读和理解。"
    
    formatted_text = text_processor.format_text(long_text, max_line_length=30)
    print("原始文本:")
    print(long_text)
    print("\n格式化后:")
    print(formatted_text)
    
    # 7. 批量处理示例
    print("\n=== 批量处理示例 ===")
    batch_texts = [
        "第一个文本",
        "第二个文本",
        "第三个文本"
    ]
    
    print("批量处理文本...")
    for text in batch_texts:
        processed = text_processor.normalize_text(text)
        print(f"处理: {text} -> {processed}")
    
    print("\n示例运行完成！")


if __name__ == "__main__":
    main() 