import asyncio
import json
import logging
import os
import re
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from docker_manager import DockerManager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Docker镜像转换工具")

# 挂载静态文件
from pathlib import Path
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

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

def parse_image_name(image_name: str) -> tuple[str, str, str, str]:
    """
    解析镜像名称，返回 (registry, bucket, name, tag)
    
    支持的格式:
    - name:tag -> (docker.io, library, name, tag)
    - name -> (docker.io, library, name, latest)
    - library/name:tag -> (docker.io, library, name, tag)
    - library/name -> (docker.io, library, name, latest)
    - registry/name:tag -> (registry, library, name, tag)
    - registry/name -> (registry, library, name, latest)
    - registry/bucket/name:tag -> (registry, bucket, name, tag)
    - registry/bucket/name -> (registry, bucket, name, latest)
    """
    # 分离tag
    if ':' in image_name:
        name_part, tag = image_name.rsplit(':', 1)
    else:
        name_part = image_name
        tag = "latest"
    
    # 解析路径部分
    parts = name_part.split('/')
    
    if len(parts) == 1:
        # name 或 name:tag
        return "docker.io", "library", parts[0], tag
    elif len(parts) == 2:
        # 检查是否是 library/name 格式
        if parts[0] == "library":
            # library/name -> (docker.io, library, name, tag)
            return "docker.io", "library", parts[1], tag
        else:
            # registry/name -> (registry, library, name, tag)
            return parts[0], "library", parts[1], tag
    elif len(parts) == 3:
        # registry/bucket/name 或 registry/bucket/name:tag
        return parts[0], parts[1], parts[2], tag
    else:
        # 不支持更多层级
        raise ValueError(f"不支持的镜像名称格式: {image_name}")

def build_source_image_name(registry: str, bucket: str, name: str, tag: str) -> str:
    """构建源镜像名称"""
    # 如果registry是docker.io且bucket是library，则省略registry
    if registry == "docker.io" and bucket == "library":
        return f"{name}:{tag}"
    # 如果只有registry和name（bucket是library），则省略bucket
    elif bucket == "library":
        return f"{registry}/{name}:{tag}"
    else:
        return f"{registry}/{bucket}/{name}:{tag}"

def build_target_image_name(new_domain: str, bucket: str, name: str, tag: str) -> str:
    """构建目标镜像名称"""
    # 目标镜像总是包含bucket，如果没有则使用library
    if not bucket or bucket == "library":
        return f"{new_domain}/library/{name}:{tag}"
    else:
        return f"{new_domain}/{bucket}/{name}:{tag}"

async def process_docker_image(image_name: str, new_domain: str):
    """处理Docker镜像：拉取、重标签、推送"""
    try:
        # 解析镜像名称
        try:
            registry, bucket, name, tag = parse_image_name(image_name)
        except ValueError as e:
            await notify_progress(f"错误：{str(e)}", 0)
            return False
        
        # 构建完整的源镜像名称
        source_image = build_source_image_name(registry, bucket, name, tag)
        
        # 构建目标镜像名称
        target_image = build_target_image_name(new_domain, bucket, name, tag)
        
        await notify_progress(f"开始处理镜像: {source_image} -> {target_image}", 10)
        
        # 拉取镜像（异步操作）
        await notify_progress("正在拉取Docker镜像...", 20)
        try:
            image = await DockerManager.pull_image_async(source_image)
            await notify_progress(f"镜像拉取成功: {image.short_id}", 40)
        except Exception as e:
            error_msg = f"拉取镜像失败: {str(e)}"
            await notify_progress(error_msg, 0)
            logger.error(error_msg)
            return False
        
        # 重标签（异步操作）
        await notify_progress("正在重标签镜像...", 60)
        try:
            success = await DockerManager.tag_image_async(image, new_domain, name, tag)
            if not success:
                error_msg = "重标签失败"
                await notify_progress(error_msg, 0)
                logger.error(error_msg)
                return False
            await notify_progress("镜像重标签成功", 80)
        except Exception as e:
            error_msg = f"重标签失败: {str(e)}"
            await notify_progress(error_msg, 0)
            logger.error(error_msg)
            return False
        
        # 推送镜像（异步操作）
        await notify_progress("正在推送镜像到新地址...", 90)
        try:
            # 定义进度回调函数
            async def progress_callback(status: str):
                await notify_progress(f"推送状态: {status}", 95)
            
            success = await DockerManager.push_image_async(target_image, progress_callback)
            if not success:
                error_msg = "推送镜像失败"
                await notify_progress(error_msg, 0)
                logger.error(error_msg)
                return False
            
            await notify_progress(f"镜像处理完成！已推送到: {target_image}", 100)
            return True
            
        except Exception as e:
            error_msg = f"推送镜像失败: {str(e)}"
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
    try:
        docker_status = "healthy" if await DockerManager.test_connection_async() else "unhealthy"
        docker_info = await DockerManager.get_connection_error_info_async()
        
        return {
            "status": "ok",
            "docker": docker_status,
            "docker_info": docker_info,
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        return {
            "status": "error",
            "docker": "unknown",
            "docker_info": f"检查失败: {str(e)}",
            "timestamp": asyncio.get_event_loop().time()
        }

@app.get("/docker-status")
async def get_docker_status():
    """获取Docker状态信息"""
    try:
        # 测试连接
        is_connected = await DockerManager.test_connection_async()
        
        if is_connected:
            # 获取详细信息
            info = await DockerManager.get_docker_info_async()
            return {
                "connected": True,
                "status": "healthy",
                "info": info,
                "message": "Docker连接正常"
            }
        else:
            # 获取错误信息
            error_info = await DockerManager.get_connection_error_info_async()
            return {
                "connected": False,
                "status": "unhealthy",
                "error": error_info,
                "message": "Docker连接失败"
            }
    except Exception as e:
        return {
            "connected": False,
            "status": "error",
            "error": str(e),
            "message": "检查Docker状态时发生错误"
        }

@app.get("/", response_class=HTMLResponse)
async def get_index():
    """返回主页面"""
    html_path = Path(__file__).parent / "static" / "index.html"
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 