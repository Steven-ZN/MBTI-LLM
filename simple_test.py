"""
简单并发测试
"""

import requests
import time
import concurrent.futures

def single_request(i):
    """单个请求"""
    payload = {
        "model": "deepseek-llm:7b",
        "messages": [
            {"role": "user", "content": f"简短回答: 什么是AI? (请求{i})"}
        ],
        "stream": False,
        "options": {
            "temperature": 0.7,
            "max_tokens": 30
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
            return end - start
        else:
            return None
    except:
        return None

def test_performance():
    """测试性能"""
    print("测试Ollama并发性能...")
    
    # 串行测试
    print("串行测试 (3个请求)...")
    start_time = time.time()
    for i in range(3):
        duration = single_request(i)
        if duration:
            print(f"  请求{i}: {duration:.2f}秒")
    sequential_time = time.time() - start_time
    print(f"串行总时间: {sequential_time:.2f}秒")
    
    print()
    
    # 并发测试
    print("并发测试 (3个请求)...")
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(single_request, i) for i in range(3)]
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            try:
                duration = future.result()
                if duration:
                    print(f"  请求{i}: {duration:.2f}秒")
            except:
                print(f"  请求{i}: 失败")
    concurrent_time = time.time() - start_time
    print(f"并发总时间: {concurrent_time:.2f}秒")
    
    # 性能对比
    if concurrent_time > 0:
        speedup = sequential_time / concurrent_time
        print(f"\n性能对比:")
        print(f"  加速比: {speedup:.2f}x")
        
        if speedup > 1.5:
            print("  结论: 并发效果显著")
        elif speedup > 1.1:
            print("  结论: 有一定并发效果")
        else:
            print("  结论: 并发效果有限")
            print("  原因: Ollama可能不支持真正的并发处理")

if __name__ == "__main__":
    test_performance()