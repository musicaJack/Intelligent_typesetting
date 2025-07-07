#!/usr/bin/env python3
"""
GPU检测和测试脚本

用于检测和测试GPU设备，特别是4090D显卡的使用情况。
"""

import torch
import sys
from pathlib import Path

def check_gpu():
    """检查GPU设备"""
    print("🔍 GPU设备检测")
    print("=" * 50)
    
    if not torch.cuda.is_available():
        print("❌ 未检测到CUDA设备")
        print("请确保已安装CUDA和PyTorch GPU版本")
        return False
    
    # 获取GPU数量
    gpu_count = torch.cuda.device_count()
    print(f"✅ 检测到 {gpu_count} 个GPU设备")
    
    # 显示每个GPU的详细信息
    for i in range(gpu_count):
        print(f"\n📊 GPU {i} 详细信息:")
        print(f"   名称: {torch.cuda.get_device_name(i)}")
        
        # 显存信息
        props = torch.cuda.get_device_properties(i)
        total_memory = props.total_memory / (1024**3)
        print(f"   显存总量: {total_memory:.1f} GB")
        
        # 计算能力
        compute_capability = f"{props.major}.{props.minor}"
        print(f"   计算能力: {compute_capability}")
        
        # 多处理器数量
        print(f"   多处理器: {props.multi_processor_count}")
        
        # 当前显存使用情况
        torch.cuda.set_device(i)
        allocated = torch.cuda.memory_allocated(i) / (1024**3)
        reserved = torch.cuda.memory_reserved(i) / (1024**3)
        print(f"   当前使用: {allocated:.2f} GB (已分配) / {reserved:.2f} GB (已保留)")
    
    return True

def test_gpu_performance():
    """测试GPU性能"""
    print("\n🚀 GPU性能测试")
    print("=" * 50)
    
    if not torch.cuda.is_available():
        print("❌ 无法进行GPU性能测试")
        return
    
    device = torch.device("cuda:0")
    print(f"使用设备: {device}")
    
    # 测试张量运算
    print("\n📈 张量运算测试:")
    
    # 创建测试张量
    sizes = [1000, 2000, 4000]
    for size in sizes:
        print(f"   测试 {size}x{size} 矩阵乘法...")
        
        # 创建随机矩阵
        a = torch.randn(size, size, device=device)
        b = torch.randn(size, size, device=device)
        
        # 预热
        torch.matmul(a, b)
        torch.cuda.synchronize()
        
        # 计时
        import time
        start_time = time.time()
        
        for _ in range(10):
            result = torch.matmul(a, b)
        
        torch.cuda.synchronize()
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 10
        print(f"   平均时间: {avg_time*1000:.2f} ms")
    
    # 显存测试
    print("\n💾 显存测试:")
    torch.cuda.empty_cache()
    
    # 测试大张量分配
    try:
        # 尝试分配大张量
        sizes_mb = [100, 500, 1000, 2000]
        for size_mb in sizes_mb:
            size_bytes = size_mb * 1024 * 1024
            size_elements = size_bytes // 4  # float32 = 4 bytes
            
            try:
                tensor = torch.randn(size_elements, device=device)
                allocated = torch.cuda.memory_allocated(device) / (1024**3)
                print(f"   成功分配 {size_mb} MB 张量，总显存使用: {allocated:.2f} GB")
                del tensor
                torch.cuda.empty_cache()
            except RuntimeError as e:
                print(f"   ❌ 无法分配 {size_mb} MB 张量: {e}")
                break
    except Exception as e:
        print(f"   显存测试失败: {e}")

def test_ckip_gpu():
    """测试CKIP在GPU上的运行"""
    print("\n🧠 CKIP GPU测试")
    print("=" * 50)
    
    try:
        from src.models.ckip_processor import CkipProcessor
        
        # 测试GPU初始化
        print("正在初始化CKIP处理器 (GPU模式)...")
        processor = CkipProcessor(model_name="bert-base", device="cuda:0")
        
        # 测试文本处理
        test_text = "弗农·德思札先生在一家名叫格朗宁的公司做主管，公司生产钻机。"
        print(f"测试文本: {test_text}")
        
        result = processor.process_text(test_text)
        
        print("✅ CKIP GPU测试成功!")
        print(f"分词结果: {len(result['tokens'])} 个词元")
        print(f"实体识别: {len(result['entities'])} 个实体")
        
        # 显示GPU使用情况
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated(0) / (1024**3)
            reserved = torch.cuda.memory_reserved(0) / (1024**3)
            print(f"GPU显存使用: {allocated:.2f} GB (已分配) / {reserved:.2f} GB (已保留)")
        
    except ImportError:
        print("❌ 无法导入CKIP处理器，请确保已安装依赖")
    except Exception as e:
        print(f"❌ CKIP GPU测试失败: {e}")

def main():
    """主函数"""
    print("🎯 智能排版系统 - GPU检测和测试")
    print("=" * 60)
    
    # 检查PyTorch版本
    print(f"PyTorch版本: {torch.__version__}")
    print(f"CUDA版本: {torch.version.cuda if torch.cuda.is_available() else 'N/A'}")
    
    # GPU检测
    gpu_available = check_gpu()
    
    if gpu_available:
        # GPU性能测试
        test_gpu_performance()
        
        # CKIP GPU测试
        test_ckip_gpu()
        
        print("\n✅ GPU检测和测试完成!")
        print("\n💡 建议:")
        print("1. 使用 --device cuda:0 参数启用GPU加速")
        print("2. 对于4090D，建议使用较大的batch_size")
        print("3. 监控显存使用情况，避免OOM错误")
    else:
        print("\n❌ GPU不可用，将使用CPU模式")
        print("💡 建议安装CUDA和PyTorch GPU版本以获得更好的性能")

if __name__ == "__main__":
    main() 