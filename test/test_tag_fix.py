#!/usr/bin/env python3
"""
测试tag_image修复后的功能
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from docker_manager import DockerManager
import docker

def test_tag_image():
    """测试tag_image方法"""
    print("🔍 测试tag_image方法...")
    
    try:
        # 创建一个模拟的image对象
        class MockImage:
            def __init__(self, short_id="test123"):
                self.short_id = short_id
                self.tags = []
            
            def tag(self, repository, tag=None):
                print(f"   调用tag: repository={repository}, tag={tag}")
                # 模拟tag操作
                new_tag = f"{repository}:{tag}" if tag else repository
                self.tags.append(new_tag)
                print(f"   添加标签: {new_tag}")
                return True
        
        # 测试参数
        image = MockImage()
        new_domain = "localhost:5000"
        bucket = "library"
        name = "nginx"
        
        print(f"   测试参数: new_domain={new_domain}, bucket={bucket}, name={name}")
        
        # 调用tag_image
        result = DockerManager.tag_image(image, new_domain, bucket, name)
        
        print(f"   结果: {result}")
        print(f"   镜像标签: {image.tags}")
        
        if result and len(image.tags) > 0:
            print("✅ tag_image测试通过")
            return True
        else:
            print("❌ tag_image测试失败")
            return False
            
    except Exception as e:
        print(f"❌ tag_image测试异常: {e}")
        return False

def test_async_tag_image():
    """测试异步tag_image方法"""
    print("\n🔍 测试异步tag_image方法...")
    
    try:
        import asyncio
        
        async def async_test():
            # 创建一个模拟的image对象
            class MockImage:
                def __init__(self, short_id="test123"):
                    self.short_id = short_id
                    self.tags = []
                
                def tag(self, repository, tag=None):
                    print(f"   调用tag: repository={repository}, tag={tag}")
                    # 模拟tag操作
                    new_tag = f"{repository}:{tag}" if tag else repository
                    self.tags.append(new_tag)
                    print(f"   添加标签: {new_tag}")
                    return True
            
            # 测试参数
            image = MockImage()
            new_domain = "localhost:5000"
            bucket = "library"
            name = "nginx"
            
            print(f"   测试参数: new_domain={new_domain}, bucket={bucket}, name={name}")
            
            # 调用异步tag_image
            result = await DockerManager.tag_image_async(image, new_domain, bucket, name)
            
            print(f"   结果: {result}")
            print(f"   镜像标签: {image.tags}")
            
            if result and len(image.tags) > 0:
                print("✅ 异步tag_image测试通过")
                return True
            else:
                print("❌ 异步tag_image测试失败")
                return False
        
        # 运行异步测试
        return asyncio.run(async_test())
        
    except Exception as e:
        print(f"❌ 异步tag_image测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 测试tag_image修复")
    print("=" * 50)
    
    # 测试同步版本
    sync_result = test_tag_image()
    
    # 测试异步版本
    async_result = test_async_tag_image()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果:")
    print(f"   同步tag_image: {'✅ 通过' if sync_result else '❌ 失败'}")
    print(f"   异步tag_image: {'✅ 通过' if async_result else '❌ 失败'}")
    
    if sync_result and async_result:
        print("\n🎉 所有测试通过！tag_image修复成功")
        return True
    else:
        print("\n❌ 部分测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 