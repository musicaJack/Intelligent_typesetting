# 🚀 快速开始指南

本指南将帮助您在5分钟内快速上手CKIP智能排版系统。

## 📋 前置要求

- Python 3.8+
- 网络连接（用于下载模型）
- 至少2GB可用内存

## ⚡ 快速安装

### 方法1: 自动安装脚本（推荐）

```bash
# 运行自动安装脚本
python install_ckip.py
```

### 方法2: 手动安装

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 验证安装
python test_ckip.py
```

## 🎯 5分钟快速体验

### 1. 基础测试

```bash
# 运行基础测试
python test_ckip.py
```

您应该看到类似输出：
```
🚀 CKIP处理器测试
==================================================
🧪 开始测试CKIP处理器...
📦 正在初始化CKIP处理器...
🔍 正在处理测试文本...

✅ 处理成功!
📝 原始文本: 弗农·德思札先生在一家名叫格朗宁的公司做主管，公司生产钻机。
🔤 Token数量: 15
🏷️ 实体数量: 2

📋 分词结果:
   1. 弗农(Nb)
   2. ·德思札(PERIODCATEGORY)
   3. 先生(Na)
   ...
```

### 2. 处理您的文本文件

```bash
# 处理文本文件并生成排版JSON
python -m src.cli ckip-typeset files/input.txt -o my_output.json
```

### 3. 查看完整演示

```bash
# 运行完整演示
python examples/ckip_typesetting_demo.py
```

## 📝 基本使用

### 命令行使用

```bash
# 基本用法
python -m src.cli ckip-typeset input.txt

# 自定义输出文件
python -m src.cli ckip-typeset input.txt -o output.json

# 自定义排版参数
python -m src.cli ckip-typeset input.txt \
    --chars-per-line 40 \
    --lines-per-page 20 \
    --output custom.json
```

### Python代码使用

```python
from src.models.ckip_processor import CkipProcessor

# 初始化处理器
processor = CkipProcessor(model_name="bert-base")

# 处理文本
text = "弗农·德思札先生在一家名叫格朗宁的公司做主管。"
result = processor.process_text(text)

# 生成排版JSON
processor.create_layout_json(text, "output.json")
```

## 📊 输出示例

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

### 排版JSON输出
```json
{
  "metadata": {
    "title": "智能排版文本",
    "total_pages": 1,
    "chars_per_line": 35,
    "lines_per_page": 18,
    "total_chars": 105
  },
  "pages": [
    {
      "page_id": 1,
      "lines": [
        {
          "text": "弗农·德思札先生在一家名叫格朗宁的",
          "offset": 0,
          "length": 15
        },
        {
          "text": "公司做主管，公司生产钻机。他高大",
          "offset": 15,
          "length": 15
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

## 🔧 常见问题

### Q: 首次运行很慢？
A: 首次运行需要下载模型文件（约500MB），请耐心等待。后续运行会使用缓存的模型。

### Q: 内存不足？
A: 确保有至少2GB可用内存。可以尝试关闭其他程序释放内存。

### Q: 网络连接问题？
A: 模型下载需要稳定的网络连接。如果下载失败，可以重试或使用国内镜像源。

### Q: 如何自定义排版参数？
A: 可以通过命令行参数或Python代码设置：
```python
processor = CkipProcessor()
processor.chars_per_line = 40  # 每行40字符
processor.lines_per_page = 20  # 每页20行
```

## 📚 下一步

- 📖 阅读完整文档: [README.md](README.md)
- 🧪 运行更多测试: `python test_ckip.py`
- 🎯 查看高级功能: `python examples/ckip_typesetting_demo.py`
- 🔧 自定义配置: 修改 `config/config.yaml`

## 🆘 获取帮助

- 📧 提交Issue: [GitHub Issues](https://github.com/your-repo/issues)
- 📖 查看文档: [完整文档](README.md)
- 💬 社区讨论: [GitHub Discussions](https://github.com/your-repo/discussions)

---

🎉 **恭喜！您已经成功上手CKIP智能排版系统！** 