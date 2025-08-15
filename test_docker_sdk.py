#!/usr/bin/env python3
"""
测试Docker SDK功能的脚本
"""

import docker
import sys

def test_docker_connection():
    """测试Docker连接"""
    try:
        client = docker.from_env()
        print("✅ Docker客户端初始化成功")
        
        # 测试连接
        client.ping()
        print("✅ Docker守护进程连接正常")
        
        # 获取Docker信息
        info = client.info()
        print(f"✅ Docker版本: {info.get('ServerVersion', 'Unknown')}")
        print(f"✅ 操作系统: {info.get('OperatingSystem', 'Unknown')}")
        
        # 列出本地镜像
        images = client.images.list()
        print(f"✅ 本地镜像数量: {len(images)}")
        
        return True
        
    except docker.errors.DockerException as e:
        print(f"❌ Docker连接失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

def test_image_operations():
    """测试镜像操作"""
    try:
        client = docker.from_env()
        
        # 测试拉取一个小镜像
        print("\n🐳 测试镜像拉取...")
        image = client.images.pull("hello-world:latest")
        print(f"✅ 成功拉取镜像: {image.short_id}")
        
        # 测试重标签
        print("\n🏷️  测试镜像重标签...")
        image.tag("test-registry", "hello-world", tag="test")
        print("✅ 镜像重标签成功")
        
        # 清理测试镜像
        print("\n🧹 清理测试镜像...")
        client.images.remove("test-registry/hello-world:test", force=True)
        print("✅ 测试镜像清理完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 镜像操作测试失败: {e}")
        return False

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