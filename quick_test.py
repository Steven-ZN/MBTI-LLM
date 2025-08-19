"""
快速测试程序 - 验证gpt-oss模型是否正常工作
"""

import requests

def test_basic():
    """基础测试"""
    print("测试deepseek-llm:7b模型...")
    
    payload = {
        "model": "deepseek-llm:7b",
        "messages": [
            {"role": "user", "content": "你好，请简单介绍一下自己"}
        ],
        "stream": False
    }
    
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json=payload,
            timeout=120  # 增加超时时间
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("message", {}).get("content", "")
            print("模型响应:")
            print(content)
            return True
        else:
            print(f"请求失败: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"测试失败: {e}")
        return False

if __name__ == "__main__":
    if test_basic():
        print("\ndeepseek-llm:7b测试成功！可以运行 python main.py")
    else:
        print("\n模型测试失败！请检查Ollama服务")