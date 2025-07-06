FROM python:3.9-slim

WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app

# 暴露端口（如果需要API服务）
EXPOSE 8000

# 默认命令
CMD ["python", "-m", "src.cli", "--help"] 