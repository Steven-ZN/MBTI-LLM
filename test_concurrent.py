"""
测试并发性能
"""

import requests
import time
import concurrent.futures
import threading

def single_request(i):
    """单个请求"""
    payload = {
        "model": "gpt-oss:20b",
        "messages": [
            {"role": "user", "content": f"请用一句话回答：什么是人工智能？(请求{i})"}
        ],
        "stream": False,
        "options": {
            "temperature": 0.7 + (i * 0.1),
            "max_tokens": 50
        }
    }
    
    start = time.time()
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json=payload,
            timeout=60
        )
        end = time.time()
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("message", {}).get("content", "")
            return f"请求{i}: {end-start:.2f}秒 - {content[:30]}..."
        else:
            return f"请求{i}: 失败 {response.status_code}"
    except Exception as e:
        return f"请求{i}: 异常 {e}"

def test_sequential():
    """测试串行请求"""
    print("🔄 测试串行请求 (5个)...")
    start_time = time.time()
    
    results = []
    for i in range(5):
        result = single_request(i)
        results.append(result)
        print(f"  {result}")
    
    end_time = time.time()
    print(f"串行总耗时: {end_time - start_time:.2f}秒\n")
    return end_time - start_time

def test_concurrent():
    """测试并发请求"""
    print("⚡ 测试并发请求 (5个)...")
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(single_request, i) for i in range(5)]
        results = []
        
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
                print(f"  {result}")
            except Exception as e:
                print(f"  请求失败: {e}")
    
    end_time = time.time()
    print(f"并发总耗时: {end_time - start_time:.2f}秒\n")
    return end_time - start_time

def main():
    print("GPU利用率测试 - Ollama并发性能")
    print("=" * 40)
    
    # 串行测试
    sequential_time = test_sequential()
    
    # 并发测试
    concurrent_time = test_concurrent()
    
    # 性能对比
    speedup = sequential_time / concurrent_time if concurrent_time > 0 else 0
    print(f"📊 性能对比:")
    print(f"  串行: {sequential_time:.2f}秒")
    print(f"  并发: {concurrent_time:.2f}秒")
    print(f"  加速比: {speedup:.2f}x")
    
    if speedup > 1.5:
        print("✅ 并发效果显著，GPU利用率得到提升")
    elif speedup > 1.1:
        print("⚠️ 并发有一定效果，可能受限于模型大小")
    else:
        print("❌ 并发效果不明显，可能是Ollama单例限制")
        print("💡 建议:")
        print("  1. 检查GPU内存是否充足")
        print("  2. 调整Ollama配置允许更多并发")
        print("  3. 尝试更小的模型进行测试")

if __name__ == "__main__":
    main()