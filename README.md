# 智能排版系统 (Intelligent Typesetting)

基于CKIP Transformers引擎的中文文本智能排版系统，支持分词、词性标注、实体识别和智能排版生成。

## 🚀 特性

- **CKIP Transformers引擎**: 使用先进的BERT模型进行中文文本处理
- **智能分词**: 准确识别中文词边界和词性
- **实体识别**: 自动识别人名、地名、组织机构等命名实体
- **智能排版**: 根据每行35字、每页18行的标准进行格式化排版
- **多格式输出**: 支持JSON和TXT两种输出格式
- **结构化标签**: TXT格式包含MCU友好的结构化标签，支持快速检索
- **标点优化**: 智能处理标点符号，避免行首出现标点
- **实体保护**: 确保命名实体在排版中不被拆分
- **MCU优化**: 专为小屏幕设备（如ST7306、RP2040）优化

## 📋 系统流程

```
输入文本文件 → CKIP Transformers引擎 → 智能排版引擎 → 多格式输出
     ↓              ↓                    ↓              ↓
  文本读取      分词+词性+实体        页面布局生成     JSON/TXT格式
```

### 核心处理阶段

1. **文本输入与预处理**: 流式读取文本文件，避免内存溢出
2. **CKIP智能处理**: 
   - 中文分词 (Word Segmentation)
   - 词性标注 (Part-of-Speech Tagging)  
   - 命名实体识别 (Named Entity Recognition)
3. **智能排版处理**: 
   - 基于语义信息的智能换行
   - 标点避头尾规则处理
   - 实体完整性保护
   - 分页优化
4. **多格式输出**: 支持JSON和TXT格式，TXT格式包含结构化标签供MCU快速检索

## 🛠️ 安装

### 环境要求

- Python 3.8+
- PyTorch 1.12+
- CUDA (可选，用于GPU加速)

### 安装步骤

1. 克隆项目
```bash
git clone <repository-url>
cd Intelligent_typesetting
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 验证安装
```bash
python test_ckip.py
```

## 📖 使用方法

### 命令行使用

#### 基础文本处理
```bash
# 处理文本文件并生成排版JSON
python -m src.cli ckip-typeset files/input.txt -o output.json

# 生成TXT格式（推荐用于MCU）
python -m src.cli ckip-typeset files/input.txt -o output.txt -f txt

# 自定义排版参数
python -m src.cli ckip-typeset files/input.txt \
    --chars-per-line 40 \
    --lines-per-page 20 \
    --output custom_layout.json

# 小屏幕设备优化（ST7306等）
python -m src.cli small-screen files/input.txt -o small_screen.txt
```

#### 其他功能
```bash
# 显示应用信息
python -m src.cli info

# 批量处理文件
python -m src.cli batch-process input_dir/ --pattern "*.txt"
```

### Python API使用

#### 基础文本处理
```python
from src.models.ckip_processor import CkipProcessor

# 初始化处理器
processor = CkipProcessor(model_name="bert-base")

# 处理文本
text = "弗农·德思札先生在一家名叫格朗宁的公司做主管。"
result = processor.process_text(text)

# 查看分词结果
for token in result["tokens"]:
    print(f"{token['text']}({token['pos']})")

# 查看实体识别结果
for entity in result["entities"]:
    print(f"{entity['text']} ({entity['type']})")
```

#### 生成排版JSON
```python
# 生成排版JSON文件
layout_result = processor.create_layout_json(text, "output.json")

print(f"生成页数: {layout_result['metadata']['total_pages']}")
print(f"总字符数: {layout_result['metadata']['total_chars']}")
```

#### 处理文件
```python
# 处理整个文件生成JSON
result = processor.process_file("input.txt", "output.json")

# 处理文件生成TXT格式
result = processor.process_file_txt("input.txt", "output.txt")
```

### 演示脚本

运行完整演示：
```bash
python examples/ckip_typesetting_demo.py
```

运行测试：
```bash
python test_ckip.py
```

## 📊 输出格式

### JSON格式（适合复杂应用）
```json
{
  "metadata": {
    "title": "智能排版文本",
    "total_pages": 5,
    "chars_per_line": 35,
    "lines_per_page": 18,
    "total_chars": 3150
  },
  "pages": [
    {
      "page_id": 1,
      "lines": [
        {
          "text": "弗农·德思札先生在一家名叫格朗宁的",
          "offset": 0,
          "length": 15,
          "tokens": [...]
        }
      ],
      "entities": [
        {
          "text": "格朗宁",
          "type": "ORG",
          "start": 8,
          "end": 11,
          "line_idx": 0
        }
      ]
    }
  ]
}
```

### 字段说明

- **metadata**: 文件元信息
  - `title`: 文档标题
  - `total_pages`: 总页数
  - `chars_per_line`: 每行字符数
  - `lines_per_page`: 每页行数
  - `total_chars`: 总字符数

- **pages**: 页面数组
  - `page_id`: 页面编号
  - `lines`: 行信息数组
    - `text`: 行文本内容
    - `offset`: 在原文中的偏移量
    - `length`: 行长度
    - `tokens`: 词元信息
  - `entities`: 实体信息数组
    - `text`: 实体文本
    - `type`: 实体类型 (PERSON/ORG/LOCATION等)
    - `start/end`: 在行中的位置
    - `line_idx`: 所在行索引

## ⚙️ 配置

### 模型配置
- **模型名称**: 默认使用 `bert-base`
- **设备**: 自动检测CPU/GPU
- **缓存目录**: 模型文件缓存位置

### 排版配置
- **每行字符数**: 默认35个中文字符
- **每页行数**: 默认18行
- **标点处理**: 自动避免行首标点
- **实体保护**: 确保命名实体不被拆分

## 🔧 高级功能

### 自定义排版规则
```python
processor = CkipProcessor(model_name="bert-base")
processor.chars_per_line = 40  # 自定义每行字符数
processor.lines_per_page = 20  # 自定义每页行数
```

### 实体类型支持
- **PERSON**: 人名 (如: 弗农·德思札)
- **ORG**: 组织机构 (如: 格朗宁公司)
- **LOCATION**: 地名
- **DATE**: 日期
- **TIME**: 时间

### 标点符号处理
- 自动标准化中英文标点
- 避免行首出现标点符号
- 支持复杂标点组合

## 🚀 性能优化

### 内存优化
- 流式文本处理，避免大文件内存溢出
- 轻量化JSON结构，减少文件体积
- 按需加载模型组件

### 速度优化
- 批量处理支持
- GPU加速 (如果可用)
- 模型缓存机制

### MCU兼容性
- 最小化JSON字段名
- 偏移量定位，支持按需读取
- 实体位置标记，便于高亮显示

### TXT格式（推荐用于MCU）
- 结构化标签，支持快速检索
- 轻量化存储，适合小内存设备
- 直接文本渲染，无需解析
- 详细说明请参考 [output_txt.README.md](output_txt.README.md)

## 📝 示例

### 输入文本
```
弗农·德思札先生在一家名叫格朗宁的公司做主管，公司生产钻机。他高大魁梧，胖得几乎连脖子都没有，却蓄着一脸大胡子。
```

### 分词结果
```
弗农(Nb) ·德思札(PERIODCATEGORY) 先生(Na) 在(P) 一(Neu) 家(Nf) 名叫(VG) 格朗宁(Nb) 的(DE) 公司(Nc) 做(VG) 主管(Na) ...
```

### 实体识别
```
• 弗农·德思札 (PERSON)
• 格朗宁 (ORG)
```

### 排版输出
```
第1行: 弗农·德思札先生在一家名叫格朗宁的
第2行: 公司做主管，公司生产钻机。他高大
第3行: 魁梧，胖得几乎连脖子都没有，却蓄
...
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

本项目采用MIT许可证。

## 🙏 致谢

- [CKIP Transformers](https://github.com/ckiplab/ckip-transformers) - 中文NLP工具包
- [Transformers](https://github.com/huggingface/transformers) - Hugging Face Transformers库
- [PyTorch](https://pytorch.org/) - 深度学习框架
