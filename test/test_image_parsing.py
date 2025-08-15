#!/usr/bin/env python3
"""
测试镜像名称解析逻辑
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import parse_image_name, build_source_image_name, build_target_image_name

def test_image_parsing():
    """测试镜像名称解析"""
    test_cases = [
        # (输入, 期望的registry, 期望的bucket, 期望的name, 期望的tag)
        ("nginx:latest", "docker.io", "library", "nginx", "latest"),
        ("ubuntu", "docker.io", "library", "ubuntu", "latest"),
        ("redis:6.0", "docker.io", "library", "redis", "6.0"),
        ("library/nginx:latest", "docker.io", "library", "nginx", "latest"),
        ("library/ubuntu", "docker.io", "library", "ubuntu", "latest"),
        ("docker.io/nginx:1.21", "docker.io", "library", "nginx", "1.21"),
        ("gcr.io/google-samples/hello-app:1.0", "gcr.io", "google-samples", "hello-app", "1.0"),
        ("quay.io/prometheus/prometheus:v2.40.0", "quay.io", "prometheus", "prometheus", "v2.40.0"),
        ("my-registry.com/my-project/app:v1.0", "my-registry.com", "my-project", "app", "v1.0"),
        ("localhost:5000/test/image:dev", "localhost:5000", "test", "image", "dev"),
    ]
    
    print("🔍 测试镜像名称解析...")
    print("=" * 60)
    
    all_passed = True
    
    for i, (input_name, exp_registry, exp_bucket, exp_name, exp_tag) in enumerate(test_cases, 1):
        try:
            registry, bucket, name, tag = parse_image_name(input_name)
            
            if (registry == exp_registry and bucket == exp_bucket and 
                name == exp_name and tag == exp_tag):
                print(f"✅ 测试 {i}: {input_name}")
                print(f"   解析结果: registry={registry}, bucket={bucket}, name={name}, tag={tag}")
            else:
                print(f"❌ 测试 {i}: {input_name}")
                print(f"   期望: registry={exp_registry}, bucket={exp_bucket}, name={exp_name}, tag={exp_tag}")
                print(f"   实际: registry={registry}, bucket={bucket}, name={name}, tag={tag}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ 测试 {i}: {input_name} - 解析失败: {e}")
            all_passed = False
        
        print()
    
    return all_passed

def test_image_building():
    """测试镜像名称构建"""
    test_cases = [
        # (registry, bucket, name, tag, 期望的源镜像, 期望的目标镜像)
        ("docker.io", "library", "nginx", "latest", "nginx:latest", "localhost:5000/library/nginx:latest"),
        ("docker.io", "library", "ubuntu", "20.04", "ubuntu:20.04", "localhost:5000/library/ubuntu:20.04"),
        ("gcr.io", "google-samples", "hello-app", "1.0", "gcr.io/google-samples/hello-app:1.0", "localhost:5000/google-samples/hello-app:1.0"),
        ("quay.io", "prometheus", "prometheus", "v2.40.0", "quay.io/prometheus/prometheus:v2.40.0", "localhost:5000/prometheus/prometheus:v2.40.0"),
        ("my-registry.com", "my-project", "app", "v1.0", "my-registry.com/my-project/app:v1.0", "localhost:5000/my-project/app:v1.0"),
    ]
    
    print("🔍 测试镜像名称构建...")
    print("=" * 60)
    
    all_passed = True
    
    for i, (registry, bucket, name, tag, exp_source, exp_target) in enumerate(test_cases, 1):
        try:
            source_image = build_source_image_name(registry, bucket, name, tag)
            target_image = build_target_image_name("localhost:5000", bucket, name, tag)
            
            if source_image == exp_source and target_image == exp_target:
                print(f"✅ 测试 {i}: {registry}/{bucket}/{name}:{tag}")
                print(f"   源镜像: {source_image}")
                print(f"   目标镜像: {target_image}")
            else:
                print(f"❌ 测试 {i}: {registry}/{bucket}/{name}:{tag}")
                print(f"   期望源镜像: {exp_source}")
                print(f"   实际源镜像: {source_image}")
                print(f"   期望目标镜像: {exp_target}")
                print(f"   实际目标镜像: {target_image}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ 测试 {i}: {registry}/{bucket}/{name}:{tag} - 构建失败: {e}")
            all_passed = False
        
        print()
    
    return all_passed

def main():
    """主测试函数"""
    print("🚀 镜像名称解析测试")
    print("=" * 60)
    
    # 测试解析
    parsing_passed = test_image_parsing()
    
    # 测试构建
    building_passed = test_image_building()
    
    # 总结
    print("=" * 60)
    print("📊 测试结果:")
    print(f"   解析测试: {'✅ 通过' if parsing_passed else '❌ 失败'}")
    print(f"   构建测试: {'✅ 通过' if building_passed else '❌ 失败'}")
    
    if parsing_passed and building_passed:
        print("\n🎉 所有测试通过！")
        return True
    else:
        print("\n❌ 部分测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 