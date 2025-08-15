#!/usr/bin/env python3
"""
启动脚本
"""

import uvicorn
from main import app

if __name__ == "__main__":
    print("🐳 启动Docker镜像转换工具...")
    print("📡 访问地址: http://localhost:8000")
    print("🔍 健康检查: http://localhost:8000/health")
    print("⏹️  按 Ctrl+C 停止应用")
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 