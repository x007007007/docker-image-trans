"""
统一的Docker客户端管理器
提供同步和异步操作接口，支持安全的客户端生命周期管理
"""

import asyncio
import contextlib
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from typing import Callable
from typing import Generator
from typing import Optional

import docker

logger = logging.getLogger(__name__)

# 创建线程池执行器
_thread_pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="docker_worker")


class DockerManager:
    """统一的Docker管理器，支持同步和异步操作"""
    
    @staticmethod
    @contextlib.contextmanager
    def get_client() -> Generator[docker.DockerClient, None, None]:
        """
        获取Docker客户端的上下文管理器（同步）
        
        使用方法:
        with DockerManager.get_client() as client:
            client.images.list()
        """
        client = None
        try:
            client = docker.from_env()
            logger.debug("Docker客户端创建成功")
            yield client
        except docker.errors.DockerException as e:
            logger.error(f"创建Docker客户端失败: {e}")
            raise
        except Exception as e:
            logger.error(f"Docker客户端操作异常: {e}")
            raise
        finally:
            if client:
                try:
                    client.close()
                    logger.debug("Docker客户端已关闭")
                except Exception as e:
                    logger.warning(f"关闭Docker客户端时出现警告: {e}")
    
    # ==================== 连接管理 ====================
    
    @staticmethod
    def test_connection() -> bool:
        """同步测试Docker连接"""
        try:
            with DockerManager.get_client() as client:
                client.ping()
                return True
        except Exception as e:
            logger.error(f"Docker连接测试失败: {e}")
            return False
    
    @staticmethod
    async def test_connection_async() -> bool:
        """异步测试Docker连接"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_thread_pool, DockerManager.test_connection)
    
    @staticmethod
    def get_connection_error_info() -> str:
        """同步获取连接错误信息"""
        try:
            with DockerManager.get_client() as client:
                client.ping()
                return "Docker连接正常"
        except FileNotFoundError:
            return "Docker服务未运行，请启动Docker Desktop或Docker服务"
        except ConnectionRefusedError:
            return "Docker守护进程拒绝连接，请检查Docker服务状态"
        except Exception as e:
            return f"Docker连接失败: {str(e)}"
    
    @staticmethod
    async def get_connection_error_info_async() -> str:
        """异步获取连接错误信息"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_thread_pool, DockerManager.get_connection_error_info)
    
    # ==================== 信息获取 ====================
    
    @staticmethod
    def get_docker_info() -> Optional[dict]:
        """同步获取Docker信息"""
        try:
            with DockerManager.get_client() as client:
                return client.info()
        except Exception as e:
            logger.error(f"获取Docker信息失败: {e}")
            return None
    
    @staticmethod
    async def get_docker_info_async() -> Optional[dict]:
        """异步获取Docker信息"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_thread_pool, DockerManager.get_docker_info)
    
    # ==================== 镜像操作 ====================
    
    @staticmethod
    def pull_image(image_name: str) -> Any:
        """同步拉取镜像"""
        with DockerManager.get_client() as client:
            return client.images.pull(image_name)
    
    @staticmethod
    async def pull_image_async(image_name: str) -> Any:
        """异步拉取镜像"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_thread_pool, DockerManager.pull_image, image_name)
    
    @staticmethod
    def tag_image(image: Any, new_domain: str, bucket: str, name: str) -> bool:
        """同步重标签镜像"""
        try:
            # 构建完整的repository和tag
            repository = f"{new_domain}/{bucket}"
            tag = name
            logger.info(f"重标签: repository={repository}, tag={tag}")
            image.tag(repository, tag=tag)
            return True
        except Exception as e:
            logger.error(f"重标签失败: {e}")
            return False
    
    @staticmethod
    async def tag_image_async(image: Any, new_domain: str, bucket: str, name: str) -> bool:
        """异步重标签镜像"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_thread_pool, DockerManager.tag_image, image, new_domain, bucket, name)
    
    @staticmethod
    def push_image(image_name: str, progress_callback: Optional[Callable] = None) -> bool:
        """同步推送镜像"""
        try:
            with DockerManager.get_client() as client:
                push_result = client.images.push(image_name, stream=True, decode=True)
                
                for line in push_result:
                    if 'error' in line:
                        logger.error(f"推送失败: {line['error']}")
                        return False
                    elif progress_callback and 'status' in line:
                        progress_callback(line['status'])
                
                return True
        except Exception as e:
            logger.error(f"推送镜像失败: {e}")
            return False
    
    @staticmethod
    async def push_image_async(image_name: str, progress_callback: Optional[Callable] = None) -> bool:
        """异步推送镜像"""
        try:
            with DockerManager.get_client() as client:
                push_result = client.images.push(image_name, stream=True, decode=True)
                
                for line in push_result:
                    if 'error' in line:
                        logger.error(f"推送失败: {line['error']}")
                        return False
                    elif progress_callback and 'status' in line:
                        # 如果回调是异步函数，需要await
                        if asyncio.iscoroutinefunction(progress_callback):
                            await progress_callback(line['status'])
                        else:
                            # 同步回调直接调用
                            progress_callback(line['status'])
                
                return True
        except Exception as e:
            logger.error(f"推送镜像失败: {e}")
            return False
    
    # ==================== 便捷方法 ====================
    
    @staticmethod
    def list_images() -> list:
        """同步列出镜像"""
        with DockerManager.get_client() as client:
            return client.images.list()
    
    @staticmethod
    async def list_images_async() -> list:
        """异步列出镜像"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_thread_pool, DockerManager.list_images)
    
    @staticmethod
    def remove_image(image_name: str, force: bool = False) -> bool:
        """同步删除镜像"""
        try:
            with DockerManager.get_client() as client:
                client.images.remove(image_name, force=force)
                return True
        except Exception as e:
            logger.error(f"删除镜像失败: {e}")
            return False
    
    @staticmethod
    async def remove_image_async(image_name: str, force: bool = False) -> bool:
        """异步删除镜像"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_thread_pool, DockerManager.remove_image, image_name, force)


# 向后兼容的别名
DockerClientManager = DockerManager
AsyncDockerOperations = DockerManager 