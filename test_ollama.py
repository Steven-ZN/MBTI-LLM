"""
测试Ollama连接和模型调用
"""

import requests
import json

def test_ollama_api():
    """测试Ollama API基本功能"""
    print("测试Ollama API连接...")
    
    # 测试API是否可用
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("Ollama API连接成功")
            models = response.json().get("models", [])
            print(f"可用模型数量: {len(models)}")
            for model in models:
                print(f"  - {model['name']} ({model['details']['parameter_size']})")
            return True
        else:
            print(f"API响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"API连接失败: {e}")
        return False

def test_model_generation():
    """测试模型生成"""
    print("\n🤖 测试模型生成...")
    
    # 测试简单生成
    payload = {
        "model": "gpt-oss:20b",
        "messages": [
            {"role": "system", "content": "你是一个测试助手，请简洁回答。"},
            {"role": "user", "content": "请回复'测试成功'"}
        ],
        "stream": False,
        "options": {
            "temperature": 0.1,
            "max_tokens": 50
        }
    }
    
    try:
        print("📡 发送测试请求...")
        response = requests.post(
            "http://localhost:11434/api/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("message", {}).get("content", "")
            print(f"✅ 模型响应: {content}")
            return True
        else:
            print(f"❌ 生成失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 生成请求失败: {e}")
        return False

def test_personality_prompt():
    """测试人格化提示"""
    print("\n🎭 测试人格化提示...")
    
    system_prompt = """你是一个具有ENTJ人格特质的AI助手。

你是一个天生的领导者，喜欢制定计划并付诸行动。你：
- 思维逻辑清晰，善于分析问题本质
- 偏好效率和结果导向
- 表达直接有力，习惯给出明确建议
- 情绪相对稳定，理性程度较高

请严格按照以下行为规范回答：

- 使用直接、明确的表达方式，适当给出建议和指导
- 采用结论先行的结构，先给要点再详细说明
- 重视逻辑性和条理性，用数据和事实支撑观点
- 保持简洁有力，段落相对较短，节奏较快

重要提醒：
- 保持人格一致性，不要在对话中"出戏"
- 你的回答风格应该稳定体现ENTJ特质
- 专注回答用户问题，避免过度解释你的人格特征
"""
    
    payload = {
        "model": "gpt-oss:20b",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "如何提高团队工作效率？"}
        ],
        "stream": False,
        "options": {
            "temperature": 0.8,
            "top_p": 0.9
        }
    }
    
    try:
        print("🎯 测试ENTJ人格化回答...")
        response = requests.post(
            "http://localhost:11434/api/chat",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("message", {}).get("content", "")
            print(f"✅ ENTJ风格回答:")
            print("-" * 40)
            print(content)
            print("-" * 40)
            return True
        else:
            print(f"❌ 人格化生成失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 人格化测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 Ollama模型测试开始")
    print("=" * 50)
    
    tests = [
        ("API连接", test_ollama_api),
        ("基础生成", test_model_generation),
        ("人格化测试", test_personality_prompt)
    ]
    
    passed = 0
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
        else:
            print(f"\n⚠️ {test_name}失败，检查Ollama配置")
    
    print(f"\n📊 测试结果: {passed}/{len(tests)} 通过")
    
    if passed == len(tests):
        print("🎉 Ollama配置正常，可以运行MBTI-LLM!")
    else:
        print("⚠️ 部分测试失败，请检查:")
        print("1. Ollama服务是否运行: ollama serve")
        print("2. gpt-oss:20b模型是否可用")
        print("3. 网络连接是否正常")

if __name__ == "__main__":
    main()