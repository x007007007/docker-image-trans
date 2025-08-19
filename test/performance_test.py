#!/usr/bin/env python3
"""
性能测试脚本
比较同步和异步Docker操作的性能
"""

import asyncio
import os
import sys
import time

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from docker_manager import DockerManager


async def test_sync_operations():
    """测试同步操作性能"""
    print("🔍 测试同步Docker操作性能...")
    
    start_time = time.time()
    
    # 模拟多个同步操作
    operations = []
    for i in range(5):
        with DockerManager.get_client() as client:
            try:
                # 获取Docker信息（模拟操作）
                info = client.info()
                operations.append(f"操作{i+1}: 成功")
            except Exception as e:
                operations.append(f"操作{i+1}: 失败 - {e}")
    
    end_time = time.time()
    sync_duration = end_time - start_time
    
    print(f"⏱️  同步操作耗时: {sync_duration:.2f}秒")
    for op in operations:
        print(f"   {op}")
    
    return sync_duration

async def test_async_operations():
    """测试异步操作性能"""
    print("\n🔍 测试异步Docker操作性能...")
    
    start_time = time.time()
    
    # 模拟多个异步操作
    operations = []
    tasks = []
    
    for i in range(5):
        async def docker_operation(op_id):
            try:
                info = await DockerManager.get_docker_info_async()
                return f"操作{op_id}: 成功"
            except Exception as e:
                return f"操作{op_id}: 失败 - {e}"
        
        task = docker_operation(i+1)
        tasks.append(task)
    
    # 并发执行所有操作
    results = await asyncio.gather(*tasks)
    operations.extend(results)
    
    end_time = time.time()
    async_duration = end_time - start_time
    
    print(f"⏱️  异步操作耗时: {async_duration:.2f}秒")
    for op in operations:
        print(f"   {op}")
    
    return async_duration

async def test_concurrent_requests():
    """测试并发请求处理能力"""
    print("\n🔍 测试并发请求处理能力...")
    
    async def simulate_request(request_id: int):
        """模拟单个请求"""
        start_time = time.time()
        
        # 模拟Docker操作
        await asyncio.sleep(0.1)  # 模拟网络延迟
        
        # 获取Docker信息
        info = await DockerManager.get_docker_info_async()
        
        end_time = time.time()
        duration = end_time - start_time
        
        return f"请求{request_id}: {duration:.3f}秒"
    
    # 创建多个并发请求
    request_count = 10
    tasks = [simulate_request(i) for i in range(request_count)]
    
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    total_time = time.time() - start_time
    
    print(f"📊 并发处理 {request_count} 个请求:")
    print(f"   总耗时: {total_time:.2f}秒")
    print(f"   平均耗时: {total_time/request_count:.3f}秒")
    
    for result in results:
        print(f"   {result}")
    
    return total_time

async def main():
    """主测试函数"""
    print("🚀 Docker操作性能测试")
    print("=" * 60)
    
    try:
        # 测试连接
        if not await DockerManager.test_connection_async():
            print("❌ Docker连接失败，无法进行性能测试")
            return
        
        print("✅ Docker连接成功，开始性能测试\n")
        
        # 测试同步操作
        sync_time = await test_sync_operations()
        
        # 测试异步操作
        async_time = await test_async_operations()
        
        # 测试并发请求
        concurrent_time = await test_concurrent_requests()
        
        # 性能对比
        print("\n" + "=" * 60)
        print("📈 性能对比结果:")
        print(f"   同步操作: {sync_time:.2f}秒")
        print(f"   异步操作: {async_time:.2f}秒")
        print(f"   性能提升: {((sync_time - async_time) / sync_time * 100):.1f}%")
        print(f"   并发处理: {concurrent_time:.2f}秒")
        
        if async_time < sync_time:
            print("✅ 异步架构性能更优！")
        else:
            print("⚠️  异步架构性能需要优化")
        
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 