#!/usr/bin/env python3
"""
测试Docker SDK功能的脚本
"""

import asyncio
import os
import sys

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from docker_manager import DockerManager


def test_docker_connection():
    """测试Docker连接"""
    try:
        print("✅ Docker客户端初始化成功")
        
        # 测试连接
        if DockerManager.test_connection():
            print("✅ Docker守护进程连接正常")
        else:
            print("❌ Docker连接测试失败")
            return False
        
        # 获取Docker信息
        info = DockerManager.get_docker_info()
        if info:
            print(f"✅ Docker版本: {info.get('ServerVersion', 'Unknown')}")
            print(f"✅ 操作系统: {info.get('OperatingSystem', 'Unknown')}")
        else:
            print("⚠️  无法获取Docker信息")
        
        # 列出本地镜像
        with DockerManager.get_client() as client:
            images = client.images.list()
            print(f"✅ 本地镜像数量: {len(images)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

async def test_image_operations_async():
    """异步测试镜像操作"""
    try:
        # 测试拉取一个小镜像
        print("\n🐳 测试异步镜像拉取...")
        image = await DockerManager.pull_image_async("hello-world:latest")
        print(f"✅ 成功拉取镜像: {image.short_id}")
        
        # 测试重标签
        print("\n🏷️  测试异步镜像重标签...")
        success = await DockerManager.tag_image_async(image, "test-registry", "hello-world", "test")
        if success:
            print("✅ 镜像重标签成功")
        else:
            print("❌ 镜像重标签失败")
            return False
        
        # 清理测试镜像
        print("\n🧹 清理测试镜像...")
        with DockerManager.get_client() as client:
            client.images.remove("test-registry/hello-world:test", force=True)
            print("✅ 测试镜像清理完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 异步镜像操作测试失败: {e}")
        return False

def test_image_operations():
    """测试镜像操作"""
    try:
        # 测试拉取一个小镜像
        print("\n🐳 测试镜像拉取...")
        with DockerManager.get_client() as client:
            image = client.images.pull("hello-world:latest")
            print(f"✅ 成功拉取镜像: {image.short_id}")
            
            # 测试重标签
            print("\n🏷️  测试镜像重标签...")
            image.tag("test-registry", "hello-world", tag="test")
            print("✅ 镜像重标签成功")
        
        # 清理测试镜像
        print("\n🧹 清理测试镜像...")
        with DockerManager.get_client() as client:
            client.images.remove("test-registry/hello-world:test", force=True)
            print("✅ 测试镜像清理完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 镜像操作测试失败: {e}")
        return False

async def run_async_tests():
    """运行异步测试"""
    print("🔍 测试异步Docker SDK功能...")
    print("=" * 50)
    
    # 测试连接
    if not await DockerManager.test_connection_async():
        print("\n❌ Docker连接测试失败，请检查Docker服务是否运行")
        return False
    
    # 测试镜像操作
    if not await test_image_operations_async():
        print("\n❌ 异步镜像操作测试失败")
        return False
    
    print("\n🎉 所有异步测试通过！Docker SDK工作正常")
    print("=" * 50)
    return True

if __name__ == "__main__":
    print("🔍 测试Docker SDK功能...")
    print("=" * 50)
    
    # 测试连接
    if not test_docker_connection():
        print("\n❌ Docker连接测试失败，请检查Docker服务是否运行")
        sys.exit(1)
    
    # 测试镜像操作
    if not test_image_operations():
        print("\n❌ 镜像操作测试失败")
        sys.exit(1)
    
    print("\n🎉 所有测试通过！Docker SDK工作正常")
    print("=" * 50)
    
    # 运行异步测试
    print("\n" + "=" * 50)
    try:
        asyncio.run(run_async_tests())
    except Exception as e:
        print(f"❌ 异步测试失败: {e}")
        sys.exit(1) 