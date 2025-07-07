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
# 处理文本文件并生成排版TXT（推荐）
python -m src.cli ckip-typeset files/input.txt -o my_output.txt
python -m src.cli ckip-typeset files/input.txt -o test_output.txt -f txt --chars-per-line 16 --lines-per-page 12

# 使用GPU加速（推荐用于4090D显卡）
python -m src.cli ckip-typeset files/input.txt -o files/output.txt --device cuda:0 --chars-per-line 16 --lines-per-page 12

# 或生成JSON格式
python -m src.cli ckip-typeset files/input.txt -o my_output.json -f json
```

### 3. 小屏幕设备优化（ST7306等）

```bash
# 专门为小屏幕设备优化排版
python -m src.cli small-screen files/input.txt -o small_screen_output.txt

# 使用GPU加速的小屏幕排版
python -m src.cli small-screen files/input.txt -o gpu_small.txt --device cuda:0 --chars-per-line 16 --lines-per-page 12

# 自定义参数
python -m src.cli small-screen files/input.txt \
    --chars-per-line 16 \
    --lines-per-page 12 \
    --device cuda:0 \
    -o custom_small.txt
```

### 4. GPU检测和测试

```bash
# 检测GPU设备（推荐4090D用户运行）
python test_gpu.py

# 查看GPU使用情况
nvidia-smi
```

### 5. 查看完整演示

```bash
# 运行完整演示
python examples/ckip_typesetting_demo.py
```

## 📝 基本使用

### 命令行使用

```bash
# 基本用法（默认TXT格式）
python -m src.cli ckip-typeset input.txt

# 自定义输出文件
python -m src.cli ckip-typeset input.txt -o output.txt

# 使用GPU加速（推荐4090D显卡）
python -m src.cli ckip-typeset input.txt -o output.txt --device cuda:0 --chars-per-line 16 --lines-per-page 12

# 自定义排版参数
python -m src.cli ckip-typeset input.txt \
    --chars-per-line 40 \
    --lines-per-page 20 \
    --output custom.txt

# 小屏幕设备专用命令
python -m src.cli small-screen input.txt \
    --chars-per-line 16 \
    --lines-per-page 12 \
    -o small_screen.txt

# 小屏幕设备 + GPU加速
python -m src.cli small-screen input.txt \
    --chars-per-line 16 \
    --lines-per-page 12 \
    --device cuda:0 \
    -o gpu_small.txt
```

### Python代码使用

```python
from src.models.ckip_processor import CkipProcessor

# 初始化处理器
processor = CkipProcessor(model_name="bert-base")

# 设置小屏幕参数
processor.chars_per_line = 16  # 每行16字符
processor.lines_per_page = 12  # 每页12行

# 处理文本
text = "弗农·德思札先生在一家名叫格朗宁的公司做主管。"
result = processor.process_text(text)

# 生成排版TXT
processor.process_file_txt("input.txt", "output.txt")
```

## 📱 小屏幕设备优化

### ST7306屏幕参数
- 分辨率：300x400像素
- 屏幕尺寸：4.2英寸
- 建议留白：上下左右各20像素
- 可用区域：260x360像素

### 推荐设置
```bash
# 最佳小屏幕设置
python -m src.cli small-screen input.txt \
    --chars-per-line 16 \
    --lines-per-page 12 \
    -o optimized.txt
```

### 文件大小对比
- JSON格式：~24MB（包含完整元数据）
- TXT格式：~2-3MB（纯文本，适合小设备）

## 📊 输出示例

### 输入文本
```
弗农·德思札先生在一家名叫格朗宁的公司做主管，公司生产钻机。他高大魁梧，胖得几乎连脖子都没有，却蓄着一脸大胡子。
```

### 小屏幕TXT输出
```
弗农·德思札先生在一
家名叫格朗宁的公司做
主管，公司生产钻机。
他高大魁梧，胖得几乎
连脖子都没有，却蓄着
一脸大胡子。

================================
第 2 页
================================

[下一页内容...]
```

### 标准JSON输出
```json
{
  "metadata": {
    "title": "智能排版文本",
    "total_pages": 1,
    "chars_per_line": 16,
    "lines_per_page": 12,
    "total_chars": 105
  },
  "pages": [
    {
      "page_id": 1,
      "lines": [
        {
          "text": "弗农·德思札先生在一",
          "offset": 0,
          "length": 10
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

### Q: 小屏幕设备文件太大？
A: 使用TXT格式替代JSON格式，文件大小会减少90%以上：
```bash
python -m src.cli small-screen input.txt -f txt -o output.txt
```

### Q: 如何自定义排版参数？
A: 可以通过命令行参数或Python代码设置：
```python
processor = CkipProcessor()
processor.chars_per_line = 16  # 每行16字符
processor.lines_per_page = 12  # 每页12行
```

### Q: ST7306屏幕显示效果不好？
A: 建议使用以下优化设置：
- 每行字符数：14-16
- 每页行数：10-12
- 输出格式：TXT
- 字体大小：16像素

### Q: 如何启用GPU加速？
A: 使用 `--device` 参数指定GPU设备：
```bash
# 自动检测GPU
python -m src.cli ckip-typeset input.txt --device auto

# 指定GPU设备
python -m src.cli ckip-typeset input.txt --device cuda:0

# 强制使用CPU
python -m src.cli ckip-typeset input.txt --device cpu
```

### Q: 4090D显卡性能优化建议？
A: 针对4090D显卡的优化建议：
- 使用 `--device cuda:0` 启用GPU加速
- 增加batch_size到16-32
- 启用混合精度加速
- 监控显存使用情况
- 运行 `python test_gpu.py` 检测GPU状态

### Q: GPU显存不足怎么办？
A: 如果遇到显存不足问题：
- 减少batch_size
- 使用 `--device cpu` 切换到CPU模式
- 关闭其他GPU程序释放显存
- 使用较小的模型

## 📚 下一步

- 📖 阅读完整文档: [README.md](README.md)
- 🧪 运行更多测试: `python test_ckip.py`
- 🎯 查看高级功能: `python examples/ckip_typesetting_demo.py`
- 🔧 自定义配置: 修改 `config/config.yaml`
- 📱 小屏幕优化: 使用 `small-screen` 命令

## 🆘 获取帮助

- 📧 提交Issue: [GitHub Issues](https://github.com/your-repo/issues)
- 📖 查看文档: [完整文档](README.md)
- 💬 社区讨论: [GitHub Discussions](https://github.com/your-repo/discussions)

---

🎉 **恭喜！您已经成功上手CKIP智能排版系统！** 