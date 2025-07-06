# Makefile for Intelligent Typesetting Project

.PHONY: help install install-dev test lint format clean build run

# 默认目标
help:
	@echo "可用的命令:"
	@echo "  install      - 安装项目依赖"
	@echo "  install-dev  - 安装开发依赖"
	@echo "  test         - 运行测试"
	@echo "  lint         - 代码检查"
	@echo "  format       - 代码格式化"
	@echo "  clean        - 清理临时文件"
	@echo "  build        - 构建项目"
	@echo "  run          - 运行应用"

# 安装依赖
install:
	pip install -r requirements.txt

# 安装开发依赖
install-dev:
	pip install -r requirements.txt
	pip install -e .

# 运行测试
test:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

# 代码检查
lint:
	flake8 src/ tests/
	isort --check-only src/ tests/

# 代码格式化
format:
	black src/ tests/
	isort src/ tests/

# 清理临时文件
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

# 构建项目
build:
	python setup.py sdist bdist_wheel

# 运行应用
run:
	python -m src.cli --help

# 创建虚拟环境
venv:
	python -m venv venv
	@echo "虚拟环境已创建，请运行: source venv/bin/activate (Linux/Mac) 或 venv\\Scripts\\activate (Windows)"

# 安装预提交钩子
pre-commit:
	pip install pre-commit
	pre-commit install

# 运行预提交检查
pre-commit-run:
	pre-commit run --all-files

# 生成文档
docs:
	sphinx-apidoc -o docs/source src/
	cd docs && make html

# 发布到PyPI（需要配置）
publish:
	python setup.py sdist bdist_wheel
	twine upload dist/* 