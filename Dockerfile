ARG IMAGE_PUB_ROOT_URL
FROM ${IMAGE_PUB_ROOT_URL}library/python:3.12.5 AS builder
ARG PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/pip \
    pip config set global.index-url "${PIP_INDEX_URL}" \
    && pip install uv

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY pyproject.toml ./

# 创建虚拟环境并安装依赖
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install --system .

# 复制应用代码
COPY src/ ./src/

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 