import asyncio
import json
import logging
import os
import re
from typing import Optional

import docker
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化Docker客户端
try:
    docker_client = docker.from_env()
    logger.info("Docker客户端初始化成功")
except Exception as e:
    logger.error(f"Docker客户端初始化失败: {e}")
    docker_client = None

app = FastAPI(title="Docker镜像转换工具")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 存储活跃的WebSocket连接
active_connections: list[WebSocket] = []

class ImageRequest(BaseModel):
    image_name: str

async def notify_progress(message: str, progress: int = 0):
    """向所有连接的WebSocket客户端发送进度更新"""
    if active_connections:
        data = {
            "message": message,
            "progress": progress,
            "timestamp": asyncio.get_event_loop().time()
        }
        await asyncio.gather(
            *[connection.send_text(json.dumps(data, ensure_ascii=False)) 
              for connection in active_connections],
            return_exceptions=True
        )

def parse_image_name(image_name: str) -> tuple[str, str, str]:
    """解析镜像名称，返回registry, name, tag"""
    # 支持多种格式: registry/name:tag, name:tag, registry/name, name
    if '/' in image_name:
        if ':' in image_name:
            registry_name, tag = image_name.rsplit(':', 1)
            if '/' in registry_name:
                registry, name = registry_name.split('/', 1)
            else:
                registry, name = registry_name, ""
        else:
            registry_name = image_name
            if '/' in registry_name:
                registry, name = registry_name.split('/', 1)
            else:
                registry, name = registry_name, ""
            tag = "latest"
    else:
        if ':' in image_name:
            name, tag = image_name.split(':', 1)
            registry = ""
        else:
            name = image_name
            tag = "latest"
            registry = ""
    
    return registry, name, tag

async def process_docker_image(image_name: str, new_domain: str):
    """处理Docker镜像：拉取、重标签、推送"""
    if not docker_client:
        await notify_progress("错误：Docker客户端未初始化", 0)
        return False
    
    try:
        # 解析镜像名称
        registry, name, tag = parse_image_name(image_name)
        if not name:
            await notify_progress("错误：无法解析镜像名称", 0)
            return False
        
        # 构建完整的源镜像名称
        source_image = f"{registry}/{name}:{tag}" if registry else f"{name}:{tag}"
        
        # 构建目标镜像名称
        target_image = f"{new_domain}/{name}:{tag}"
        
        await notify_progress(f"开始处理镜像: {source_image} -> {target_image}", 10)
        
        # 拉取镜像
        await notify_progress("正在拉取Docker镜像...", 20)
        try:
            # 使用Docker SDK拉取镜像
            image = docker_client.images.pull(source_image)
            await notify_progress(f"镜像拉取成功: {image.short_id}", 40)
        except docker.errors.APIError as e:
            error_msg = f"拉取镜像失败: {e.explanation}"
            await notify_progress(error_msg, 0)
            logger.error(error_msg)
            return False
        
        # 重标签
        await notify_progress("正在重标签镜像...", 60)
        try:
            # 使用Docker SDK重标签
            image.tag(new_domain, name, tag=tag)
            await notify_progress("镜像重标签成功", 80)
        except docker.errors.APIError as e:
            error_msg = f"重标签失败: {e.explanation}"
            await notify_progress(error_msg, 0)
            logger.error(error_msg)
            return False
        
        # 推送镜像
        await notify_progress("正在推送镜像到新地址...", 90)
        try:
            # 使用Docker SDK推送镜像
            push_result = docker_client.images.push(target_image, stream=True, decode=True)
            
            # 处理推送流
            for line in push_result:
                if 'error' in line:
                    error_msg = f"推送失败: {line['error']}"
                    await notify_progress(error_msg, 0)
                    logger.error(error_msg)
                    return False
                elif 'status' in line:
                    await notify_progress(f"推送状态: {line['status']}", 95)
            
            await notify_progress(f"镜像处理完成！已推送到: {target_image}", 100)
            return True
            
        except docker.errors.APIError as e:
            error_msg = f"推送镜像失败: {e.explanation}"
            await notify_progress(error_msg, 0)
            logger.error(error_msg)
            return False
        
    except Exception as e:
        error_msg = f"处理过程中发生错误: {str(e)}"
        await notify_progress(error_msg, 0)
        logger.error(error_msg)
        return False

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        await notify_progress("WebSocket连接已建立", 0)
        while True:
            # 保持连接活跃
            await asyncio.sleep(30)
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        await notify_progress("WebSocket连接已断开", 0)

@app.post("/process-image")
async def process_image(request: ImageRequest):
    """处理镜像转换请求"""
    new_domain = os.getenv("NEW_DOMAIN", "localhost:5000")
    
    # 启动异步任务处理镜像
    asyncio.create_task(process_docker_image(request.image_name, new_domain))
    
    return {"message": "镜像处理已开始", "image_name": request.image_name}

@app.get("/health")
async def health_check():
    """健康检查端点"""
    docker_status = "healthy" if docker_client else "unhealthy"
    return {
        "status": "ok",
        "docker": docker_status,
        "timestamp": asyncio.get_event_loop().time()
    }

@app.get("/", response_class=HTMLResponse)
async def get_index():
    """返回主页面"""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 