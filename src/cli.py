"""
命令行接口模块

提供命令行工具，用于处理文本和调用BERT模型。
"""

import click
from pathlib import Path
from typing import Optional

from .config import Config
from .models import BertModel, TextProcessor
from .models.ckip_processor import CkipProcessor
from .utils import setup_logging, FileUtils


@click.group()
@click.option('--config', '-c', default='config/config.yaml', help='配置文件路径')
@click.option('--verbose', '-v', is_flag=True, help='详细输出')
@click.pass_context
def cli(ctx, config: str, verbose: bool):
    """智能排版应用 - 基于BERT模型的文本处理工具"""
    # 确保上下文对象存在
    ctx.ensure_object(dict)
    
    # 加载配置
    try:
        ctx.obj['config'] = Config(config)
        setup_logging(ctx.obj['config'].logging_config)
    except Exception as e:
        click.echo(f"加载配置失败: {e}", err=True)
        ctx.exit(1)
    
    # 设置日志
    log_config = ctx.obj['config'].logging_config
    if verbose:
        log_config['level'] = 'DEBUG'
    setup_logging(log_config)
    
    click.echo(f"智能排版应用 v{ctx.obj['config'].get('app.version', '0.1.0')}")


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='输出文件路径')
@click.option('--format', '-f', type=click.Choice(['txt', 'json', 'csv']), default='txt', help='输出格式')
@click.pass_context
def process(ctx, input_file: str, output: Optional[str], format: str):
    """处理文本文件"""
    config = ctx.obj['config']
    
    # 初始化组件
    bert_model = BertModel(config)
    text_processor = TextProcessor()
    file_utils = FileUtils(config.get('data.encoding', 'utf-8'))
    
    try:
        # 读取输入文件
        click.echo(f"正在读取文件: {input_file}")
        content = file_utils.read_text(input_file)
        
        # 处理文本
        click.echo("正在处理文本...")
        processed_text = text_processor.normalize_text(content)
        
        # 获取关键词
        keywords = text_processor.extract_keywords(processed_text, top_k=10)
        
        # 格式化文本
        formatted_text = text_processor.format_text(processed_text, max_line_length=80)
        
        # 准备输出
        if format == 'json':
            output_data = {
                'original_text': content,
                'processed_text': processed_text,
                'formatted_text': formatted_text,
                'keywords': keywords
            }
        elif format == 'csv':
            output_data = [{
                'original_text': content,
                'processed_text': processed_text,
                'formatted_text': formatted_text,
                'keywords': ', '.join(keywords)
            }]
        else:
            output_data = formatted_text
        
        # 确定输出路径
        if output is None:
            input_path = Path(input_file)
            output = input_path.parent / f"{input_path.stem}_processed.{format}"
        
        # 写入输出文件
        click.echo(f"正在写入输出文件: {output}")
        if format == 'json':
            file_utils.write_json(output, output_data)
        elif format == 'csv':
            file_utils.write_csv(output, output_data)
        else:
            file_utils.write_text(output, output_data)
        
        click.echo("处理完成！")
        click.echo(f"关键词: {', '.join(keywords[:5])}...")
        
    except Exception as e:
        click.echo(f"处理失败: {e}", err=True)
        ctx.exit(1)


@cli.command()
@click.argument('text1')
@click.argument('text2')
@click.pass_context
def similarity(ctx, text1: str, text2: str):
    """计算两个文本的相似度"""
    config = ctx.obj['config']
    
    # 初始化BERT模型
    bert_model = BertModel(config)
    
    try:
        click.echo("正在计算文本相似度...")
        similarity_score = bert_model.calculate_similarity(text1, text2)
        
        click.echo(f"文本相似度: {similarity_score:.4f}")
        
    except Exception as e:
        click.echo(f"计算相似度失败: {e}", err=True)
        ctx.exit(1)


@cli.command()
@click.argument('input_dir', type=click.Path(exists=True))
@click.option('--output-dir', '-o', type=click.Path(), help='输出目录')
@click.option('--pattern', '-p', default='*.txt', help='文件匹配模式')
@click.pass_context
def batch_process(ctx, input_dir: str, output_dir: Optional[str], pattern: str):
    """批量处理文件"""
    config = ctx.obj['config']
    
    # 初始化组件
    bert_model = BertModel(config)
    text_processor = TextProcessor()
    file_utils = FileUtils(config.get('data.encoding', 'utf-8'))
    
    # 确定输出目录
    if output_dir is None:
        output_dir = Path(input_dir) / 'processed'
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 获取输入文件列表
        input_files = file_utils.list_files(input_dir, pattern)
        
        if not input_files:
            click.echo(f"在目录 {input_dir} 中没有找到匹配 {pattern} 的文件")
            return
        
        click.echo(f"找到 {len(input_files)} 个文件，开始批量处理...")
        
        # 处理每个文件
        for i, input_file in enumerate(input_files, 1):
            try:
                click.echo(f"[{i}/{len(input_files)}] 处理文件: {input_file.name}")
                
                # 读取文件
                content = file_utils.read_text(input_file)
                
                # 处理文本
                processed_text = text_processor.normalize_text(content)
                formatted_text = text_processor.format_text(processed_text)
                
                # 写入输出文件
                output_file = output_dir / f"{input_file.stem}_processed.txt"
                file_utils.write_text(output_file, formatted_text)
                
            except Exception as e:
                click.echo(f"处理文件 {input_file.name} 失败: {e}", err=True)
                continue
        
        click.echo(f"批量处理完成！输出目录: {output_dir}")
        
    except Exception as e:
        click.echo(f"批量处理失败: {e}", err=True)
        ctx.exit(1)


@cli.command()
@click.pass_context
def info(ctx):
    """显示应用信息"""
    config = ctx.obj['config']
    
    click.echo("=== 智能排版应用信息 ===")
    click.echo(f"版本: {config.get('app.version', '0.1.0')}")
    click.echo(f"BERT模型: {config.get('model.bert.model_name', 'N/A')}")


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='输出JSON文件路径')
@click.option('--model', '-m', default='bert-base', help='CKIP模型名称')
@click.option('--chars-per-line', default=35, help='每行字符数')
@click.option('--lines-per-page', default=18, help='每页行数')
@click.pass_context
def ckip_typeset(ctx, input_file: str, output: str, model: str, chars_per_line: int, lines_per_page: int):
    """使用CKIP Transformers进行智能排版"""
    config = ctx.obj['config']
    
    try:
        # 初始化CKIP处理器
        click.echo(f"正在初始化CKIP处理器 (模型: {model})...")
        processor = CkipProcessor(model_name=model)
        
        # 设置排版参数
        processor.chars_per_line = chars_per_line
        processor.lines_per_page = lines_per_page
        
        # 确定输出路径
        if output is None:
            input_path = Path(input_file)
            output = input_path.parent / f"{input_path.stem}_ckip_layout.json"
        
        # 处理文件
        click.echo(f"正在处理文件: {input_file}")
        result = processor.process_file(input_file, str(output))
        
        # 显示结果
        click.echo("✅ 处理完成！")
        click.echo(f"📁 输出文件: {output}")
        click.echo(f"📊 生成页数: {result['metadata']['total_pages']}")
        click.echo(f"📏 每行字符数: {result['metadata']['chars_per_line']}")
        click.echo(f"📄 每页行数: {result['metadata']['lines_per_page']}")
        click.echo(f"📝 总字符数: {result['metadata']['total_chars']}")
        
        # 显示第一页预览
        if result["pages"]:
            first_page = result["pages"][0]
            click.echo(f"\n📄 第一页预览 (共{len(first_page['lines'])}行):")
            for i, line in enumerate(first_page['lines'][:3], 1):
                click.echo(f"  {i}. {line['text']}")
            if len(first_page['lines']) > 3:
                click.echo(f"  ... (还有{len(first_page['lines']) - 3}行)")
        
    except Exception as e:
        click.echo(f"处理失败: {e}", err=True)
        ctx.exit(1)
    click.echo(f"设备: {config.get('model.bert.device', 'N/A')}")
    click.echo(f"最大长度: {config.get('model.bert.max_length', 'N/A')}")
    click.echo(f"批处理大小: {config.get('model.bert.batch_size', 'N/A')}")
    click.echo(f"输入目录: {config.get('data.input_dir', 'N/A')}")
    click.echo(f"输出目录: {config.get('data.output_dir', 'N/A')}")
    click.echo(f"支持格式: {', '.join(config.get('data.supported_formats', []))}")


def main():
    """主函数"""
    cli(obj={})


if __name__ == '__main__':
    main() 