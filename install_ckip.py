#!/usr/bin/env python3
"""
CKIP Transformers安装脚本

自动安装CKIP Transformers和相关依赖
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """运行命令并显示进度"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description}完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False


def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 需要Python 3.8或更高版本")
        print(f"当前版本: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python版本检查通过: {version.major}.{version.minor}.{version.micro}")
    return True


def install_dependencies():
    """安装依赖"""
    print("\n📦 开始安装依赖...")
    
    # 升级pip
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "升级pip"):
        return False
    
    # 安装基础依赖
    dependencies = [
        "torch>=1.12.0",
        "transformers>=4.20.0",
        "tokenizers>=0.12.0",
        "numpy>=1.21.0",
        "pandas>=1.4.0",
        "scikit-learn>=1.1.0",
        "python-dotenv>=0.19.0",
        "pyyaml>=6.0",
        "click>=8.1.0",
        "loguru>=0.6.0",
        "tqdm>=4.64.0"
    ]
    
    for dep in dependencies:
        if not run_command(f"{sys.executable} -m pip install {dep}", f"安装{dep}"):
            return False
    
    # 安装CKIP Transformers
    if not run_command(f"{sys.executable} -m pip install ckip-transformers>=0.4.0", "安装CKIP Transformers"):
        return False
    
    return True


def test_installation():
    """测试安装"""
    print("\n🧪 测试安装...")
    
    test_code = """
import sys
try:
    from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger, CkipNerChunker
    print("✅ CKIP Transformers导入成功")
    
    # 测试初始化
    ws_driver = CkipWordSegmenter(model="bert-base")
    pos_driver = CkipPosTagger(model="bert-base")
    ner_driver = CkipNerChunker(model="bert-base")
    print("✅ CKIP模型初始化成功")
    
    # 测试文本处理
    text = "弗农·德思札先生在一家名叫格朗宁的公司做主管。"
    ws = ws_driver([text])
    pos = pos_driver(ws)
    ner = ner_driver([text])
    print("✅ 文本处理测试成功")
    
    print(f"分词结果: {ws[0][:5]}...")
    print(f"词性标注: {pos[0][:5]}...")
    print(f"实体识别: {len(ner[0])}个实体")
    
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ 测试失败: {e}")
    sys.exit(1)
"""
    
    try:
        result = subprocess.run([sys.executable, "-c", test_code], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 测试失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False


def create_directories():
    """创建必要的目录"""
    print("\n📁 创建目录结构...")
    
    directories = [
        "data/input",
        "data/output", 
        "logs",
        "models"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目录: {directory}")


def main():
    """主函数"""
    print("🚀 CKIP Transformers智能排版系统安装脚本")
    print("=" * 60)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 安装依赖
    if not install_dependencies():
        print("❌ 依赖安装失败")
        sys.exit(1)
    
    # 测试安装
    if not test_installation():
        print("❌ 安装测试失败")
        sys.exit(1)
    
    # 创建目录
    create_directories()
    
    print("\n" + "=" * 60)
    print("🎉 安装完成!")
    print("=" * 60)
    
    print("\n📋 下一步:")
    print("1. 运行测试: python test_ckip.py")
    print("2. 查看演示: python examples/ckip_typesetting_demo.py")
    print("3. 处理文件: python -m src.cli ckip-typeset files/input.txt")
    
    print("\n📖 更多信息请查看README.md")
    
    print("\n💡 提示:")
    print("- 首次运行时会自动下载模型文件")
    print("- 模型文件较大，请确保网络连接稳定")
    print("- 建议使用GPU加速处理速度")


if __name__ == "__main__":
    main() 