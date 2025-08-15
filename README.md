# Docker镜像转换工具

一个基于FastAPI和WebSocket的Docker镜像转换工具，可以拉取Docker镜像，重标签并推送到新的镜像仓库。

## 功能特性

- 🐳 支持多种Docker镜像格式
- 📡 实时WebSocket进度更新
- 🎨 现代化美观的Web界面
- ⚡ 异步处理，不阻塞用户界面
- 🔄 自动重连WebSocket连接
- 📱 响应式设计，支持移动设备
- 🛡️ 使用官方Docker Python SDK，更安全可靠
- 📊 详细的错误处理和状态反馈

## 支持的镜像格式

- `nginx:latest` - 简单名称，自动使用latest标签
- `ubuntu:20.04` - 带版本标签的名称
- `docker.io/library/nginx:1.21` - 完整仓库地址
- `gcr.io/google-samples/hello-app:1.0` - Google容器仓库
- `quay.io/prometheus/prometheus:v2.40.0` - Quay仓库

## 环境要求

- Python 3.8+
- Docker CLI
- uv包管理器

## 安装和运行

### 1. 安装依赖

```bash
# 使用uv安装依赖
uv sync
```

### 2. 设置环境变量（可选）

```bash
# 设置新的镜像仓库域名
export NEW_DOMAIN="your-registry.com:5000"

# 如果不设置，默认使用 localhost:5000
```

### 3. 运行应用

```bash
# 使用uv运行
uv run main.py

# 或者使用uvicorn直接运行
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问应用

打开浏览器访问：http://localhost:8000

## 使用方法

1. 在输入框中输入要转换的Docker镜像名称
2. 点击"开始转换"按钮
3. 系统会自动：
   - 拉取指定的Docker镜像
   - 重标签为新的域名
   - 推送到新的镜像仓库
4. 实时查看处理进度和状态信息

## 项目结构

```
image_trans/
├── main.py              # FastAPI主应用
├── static/
│   └── index.html      # 前端页面
├── pyproject.toml      # 项目配置
└── README.md           # 项目说明
```

## API接口

### WebSocket接口

- **连接地址**: `/ws`
- **功能**: 实时进度更新

### HTTP接口

- **GET** `/health`
  - 响应: `{"status": "ok", "docker": "healthy|unhealthy", "timestamp": 时间戳}`
  - 功能: 健康检查，验证Docker连接状态

- **POST** `/process-image`
  - 请求体: `{"image_name": "镜像名称"}`
  - 响应: `{"message": "处理状态", "image_name": "镜像名称"}`

## 注意事项

1. 确保Docker服务正在运行
2. 确保有足够的磁盘空间存储镜像
3. 确保有权限推送到目标镜像仓库
4. 网络连接稳定，避免镜像拉取失败

## 故障排除

### 常见问题

1. **Docker命令执行失败**
   - 检查Docker服务是否运行
   - 检查Docker CLI权限

2. **WebSocket连接失败**
   - 检查防火墙设置
   - 检查网络连接

3. **镜像推送失败**
   - 检查目标仓库权限
   - 检查网络连接

## 开发

### 安装开发依赖

```bash
uv sync --dev
```

### 代码格式化

```bash
uv run black .
uv run isort .
```

### 运行测试

```bash
uv run pytest
```

## 许可证

MIT License 