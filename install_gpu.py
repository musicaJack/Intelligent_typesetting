#!/usr/bin/env python3
"""
GPU版本安装脚本

专门为4090D显卡安装GPU版本的PyTorch和相关依赖。
"""

import subprocess
import sys
import platform
import os

def check_system():
    """检查系统环境"""
    print("🔍 系统环境检测")
    print("=" * 50)
    
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {sys.version}")
    print(f"架构: {platform.machine()}")
    
    # 检查NVIDIA驱动
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ NVIDIA驱动已安装")
            print("GPU信息:")
            lines = result.stdout.split('\n')
            for line in lines[:10]:  # 显示前10行
                if line.strip():
                    print(f"  {line}")
        else:
            print("❌ NVIDIA驱动未安装或不可用")
            return False
    except FileNotFoundError:
        print("❌ nvidia-smi命令不可用，请安装NVIDIA驱动")
        return False
    
    return True

def install_pytorch_gpu():
    """安装GPU版本的PyTorch"""
    print("\n🚀 安装GPU版本PyTorch")
    print("=" * 50)
    
    # 检测CUDA版本
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'release' in line.lower():
                    print(f"检测到CUDA: {line.strip()}")
                    break
        else:
            print("❌ CUDA未安装，请先安装CUDA Toolkit")
            return False
    except FileNotFoundError:
        print("❌ nvcc命令不可用，请安装CUDA Toolkit")
        return False
    
    # 安装PyTorch GPU版本
    print("\n📦 安装PyTorch GPU版本...")
    
    # 根据CUDA版本选择合适的安装命令
    pytorch_commands = [
        # CUDA 12.1 (推荐)
        "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121",
        # CUDA 11.8 (备选)
        "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118",
        # CUDA 12.4 (最新)
        "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124",
    ]
    
    for i, command in enumerate(pytorch_commands, 1):
        print(f"\n尝试安装命令 {i}: {command}")
        try:
            result = subprocess.run(command.split(), check=True, capture_output=True, text=True)
            print("✅ PyTorch GPU版本安装成功!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 安装失败: {e}")
            if i < len(pytorch_commands):
                print("尝试下一个安装命令...")
            else:
                print("所有安装命令都失败了")
                return False
    
    return False

def install_ckip_transformers():
    """安装CKIP Transformers"""
    print("\n📦 安装CKIP Transformers")
    print("=" * 50)
    
    try:
        # 安装CKIP Transformers
        result = subprocess.run([
            "pip", "install", "ckip-transformers"
        ], check=True, capture_output=True, text=True)
        print("✅ CKIP Transformers安装成功!")
        
        # 安装其他依赖
        dependencies = [
            "transformers>=4.20.0",
            "torch>=1.12.0",
            "numpy>=1.21.0",
            "loguru>=0.6.0",
            "click>=8.0.0",
            "pyyaml>=6.0",
        ]
        
        for dep in dependencies:
            print(f"安装依赖: {dep}")
            subprocess.run(["pip", "install", dep], check=True)
        
        print("✅ 所有依赖安装完成!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装失败: {e}")
        return False

def verify_installation():
    """验证安装"""
    print("\n✅ 验证安装")
    print("=" * 50)
    
    try:
        import torch
        print(f"PyTorch版本: {torch.__version__}")
        print(f"CUDA可用: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"CUDA版本: {torch.version.cuda}")
            print(f"GPU数量: {torch.cuda.device_count()}")
            
            for i in range(torch.cuda.device_count()):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_memory = torch.cuda.get_device_properties(i).total_memory / (1024**3)
                print(f"GPU {i}: {gpu_name}, 显存: {gpu_memory:.1f}GB")
        
        # 测试CKIP
        try:
            from ckip_transformers.nlp import CkipWordSegmenter
            print("✅ CKIP Transformers导入成功!")
        except ImportError:
            print("❌ CKIP Transformers导入失败")
            return False
        
        print("✅ 所有组件安装验证成功!")
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def main():
    """主函数"""
    print("🎯 智能排版系统 - GPU版本安装")
    print("=" * 60)
    print("本脚本将为您安装GPU版本的PyTorch和CKIP Transformers")
    print("特别针对4090D显卡进行优化")
    print("=" * 60)
    
    # 检查系统
    if not check_system():
        print("\n❌ 系统环境检查失败，请先安装NVIDIA驱动和CUDA Toolkit")
        return
    
    # 安装PyTorch GPU版本
    if not install_pytorch_gpu():
        print("\n❌ PyTorch GPU版本安装失败")
        return
    
    # 安装CKIP Transformers
    if not install_ckip_transformers():
        print("\n❌ CKIP Transformers安装失败")
        return
    
    # 验证安装
    if not verify_installation():
        print("\n❌ 安装验证失败")
        return
    
    print("\n🎉 GPU版本安装完成!")
    print("\n💡 使用建议:")
    print("1. 运行 'python test_gpu.py' 检测GPU状态")
    print("2. 使用 '--device cuda:0' 参数启用GPU加速")
    print("3. 监控显存使用情况: nvidia-smi")
    print("4. 对于4090D，建议使用较大的batch_size")
    
    print("\n🚀 现在可以开始使用GPU加速的智能排版了!")

if __name__ == "__main__":
    main() 