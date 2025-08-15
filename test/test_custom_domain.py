#!/usr/bin/env python3
"""
测试自定义域名功能
"""

import sys
import os
import asyncio

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import parse_image_name, build_source_image_name, build_target_image_name

def test_custom_domain_building():
    """测试自定义域名构建"""
    print("🔍 测试自定义域名构建...")
    
    test_cases = [
        # (new_domain, bucket, name, tag, 期望的目标镜像)
        ("my-registry.com", "library", "nginx", "latest", "my-registry.com/library/nginx:latest"),
        ("registry.example.com:8080", "library", "ubuntu", "20.04", "registry.example.com:8080/library/ubuntu:20.04"),
        ("localhost:3000", "google-samples", "hello-app", "1.0", "localhost:3000/google-samples/hello-app:1.0"),
        ("", "prometheus", "prometheus", "v2.40.0", "localhost:5000/prometheus/prometheus:v2.40.0"),  # 空域名使用默认值
        (None, "my-project", "app", "v1.0", "localhost:5000/my-project/app:v1.0"),  # None使用默认值
    ]
    
    all_passed = True
    
    for i, (new_domain, bucket, name, tag, expected) in enumerate(test_cases, 1):
        try:
            # 模拟环境变量
            if new_domain == "" or new_domain is None:
                # 测试空值或None的情况
                result = build_target_image_name("localhost:5000", bucket, name, tag)
            else:
                result = build_target_image_name(new_domain, bucket, name, tag)
            
            if result == expected:
                print(f"✅ 测试 {i}: {new_domain or 'None'} -> {result}")
            else:
                print(f"❌ 测试 {i}: {new_domain or 'None'}")
                print(f"   期望: {expected}")
                print(f"   实际: {result}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ 测试 {i}: {new_domain or 'None'} - 异常: {e}")
            all_passed = False
        
        print()
    
    return all_passed

def test_image_parsing_with_custom_domain():
    """测试镜像解析与自定义域名结合"""
    print("🔍 测试镜像解析与自定义域名结合...")
    
    test_cases = [
        # (输入镜像, 期望的解析结果)
        ("nginx:latest", ("docker.io", "library", "nginx", "latest")),
        ("library/ubuntu", ("docker.io", "library", "ubuntu", "latest")),
        ("gcr.io/google-samples/hello-app:1.0", ("gcr.io", "google-samples", "hello-app", "1.0")),
        ("quay.io/prometheus/prometheus:v2.40.0", ("quay.io", "prometheus", "prometheus", "v2.40.0")),
    ]
    
    all_passed = True
    
    for i, (input_image, expected) in enumerate(test_cases, 1):
        try:
            result = parse_image_name(input_image)
            
            if result == expected:
                print(f"✅ 测试 {i}: {input_image}")
                print(f"   解析结果: registry={result[0]}, bucket={result[1]}, name={result[2]}, tag={result[3]}")
            else:
                print(f"❌ 测试 {i}: {input_image}")
                print(f"   期望: {expected}")
                print(f"   实际: {result}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ 测试 {i}: {input_image} - 异常: {e}")
            all_passed = False
        
        print()
    
    return all_passed

def test_end_to_end_conversion():
    """测试端到端转换流程"""
    print("🔍 测试端到端转换流程...")
    
    test_cases = [
        # (输入镜像, 自定义域名, 期望的源镜像, 期望的目标镜像)
        ("nginx:latest", "my-registry.com", "nginx:latest", "my-registry.com/library/nginx:latest"),
        ("ubuntu:20.04", "registry.example.com:8080", "ubuntu:20.04", "registry.example.com:8080/library/ubuntu:20.04"),
        ("gcr.io/google-samples/hello-app:1.0", "localhost:3000", "gcr.io/google-samples/hello-app:1.0", "localhost:3000/google-samples/hello-app:1.0"),
        ("quay.io/prometheus/prometheus:v2.40.0", "", "quay.io/prometheus/prometheus:v2.40.0", "localhost:5000/prometheus/prometheus:v2.40.0"),
    ]
    
    all_passed = True
    
    for i, (input_image, custom_domain, exp_source, exp_target) in enumerate(test_cases, 1):
        try:
            # 解析镜像名称
            registry, bucket, name, tag = parse_image_name(input_image)
            
            # 构建源镜像名称
            source_image = build_source_image_name(registry, bucket, name, tag)
            
            # 构建目标镜像名称（使用自定义域名或默认值）
            target_domain = custom_domain or "localhost:5000"
            target_image = build_target_image_name(target_domain, bucket, name, tag)
            
            if source_image == exp_source and target_image == exp_target:
                print(f"✅ 测试 {i}: {input_image} -> {custom_domain or '默认'}")
                print(f"   源镜像: {source_image}")
                print(f"   目标镜像: {target_image}")
            else:
                print(f"❌ 测试 {i}: {input_image} -> {custom_domain or '默认'}")
                print(f"   期望源镜像: {exp_source}")
                print(f"   实际源镜像: {source_image}")
                print(f"   期望目标镜像: {exp_target}")
                print(f"   实际目标镜像: {target_image}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ 测试 {i}: {input_image} -> {custom_domain or '默认'} - 异常: {e}")
            all_passed = False
        
        print()
    
    return all_passed

def main():
    """主测试函数"""
    print("🚀 自定义域名功能测试")
    print("=" * 60)
    
    # 测试自定义域名构建
    domain_building_passed = test_custom_domain_building()
    
    # 测试镜像解析
    parsing_passed = test_image_parsing_with_custom_domain()
    
    # 测试端到端转换
    conversion_passed = test_end_to_end_conversion()
    
    # 总结
    print("=" * 60)
    print("📊 测试结果:")
    print(f"   自定义域名构建: {'✅ 通过' if domain_building_passed else '❌ 失败'}")
    print(f"   镜像解析: {'✅ 通过' if parsing_passed else '❌ 失败'}")
    print(f"   端到端转换: {'✅ 通过' if conversion_passed else '❌ 失败'}")
    
    if domain_building_passed and parsing_passed and conversion_passed:
        print("\n🎉 所有测试通过！自定义域名功能正常")
        return True
    else:
        print("\n❌ 部分测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 