"""
集成测试脚本
验证MBTI-LLM系统各组件功能
"""

import sys
from personality_controller import PersonalityController, quick_generate
from personality_rules import PREDEFINED_PERSONAS
from style_scorer import StyleScorer

def test_personality_rules():
    """测试人格规则库"""
    print("🧪 测试人格规则库...")
    
    try:
        for mbti_type in PREDEFINED_PERSONAS:
            profile = PREDEFINED_PERSONAS[mbti_type]
            print(f"  ✅ {mbti_type}: {profile.mbti} - E:{profile.e_score} S:{profile.s_score} T:{profile.t_score} J:{profile.j_score}")
        return True
    except Exception as e:
        print(f"  ❌ 人格规则库测试失败: {e}")
        return False

def test_style_scorer():
    """测试风格评分器"""
    print("\n🧪 测试风格评分器...")
    
    try:
        scorer = StyleScorer()
        profile = PREDEFINED_PERSONAS["ENTJ"]
        
        # 测试文本
        test_texts = [
            "我们必须立即制定战略计划，确保项目按时完成。",  # ENTJ风格
            "也许我们可以考虑一种更温和的方式来解决这个问题。",  # INFP风格
            "让我分析一下具体的技术方案和实施步骤。"  # ISTP风格
        ]
        
        for i, text in enumerate(test_texts):
            score = scorer.score_text(text, profile)
            print(f"  📝 文本{i+1}与ENTJ匹配度: {score:.3f}")
        
        print("  ✅ 风格评分器测试通过")
        return True
    except Exception as e:
        print(f"  ❌ 风格评分器测试失败: {e}")
        return False

def test_ollama_connection():
    """测试Ollama连接"""
    print("\n🧪 测试Ollama连接...")
    
    try:
        controller = PersonalityController()
        response = controller._call_ollama(
            "你是一个测试助手。", 
            "请简单回复'测试成功'",
            temperature=0.1
        )
        
        if response:
            print(f"  📡 Ollama响应: {response[:50]}...")
            print("  ✅ Ollama连接测试通过")
            return True
        else:
            print("  ⚠️  Ollama无响应，请检查服务状态")
            return False
    except Exception as e:
        print(f"  ❌ Ollama连接测试失败: {e}")
        print("  💡 请确保Ollama已启动并下载了gpt-oss:20b模型")
        return False

def test_personality_generation():
    """测试人格化生成"""
    print("\n🧪 测试人格化生成...")
    
    try:
        test_question = "什么是人工智能？"
        
        print(f"  🤔 测试问题: {test_question}")
        
        for personality in ["ENTJ"]:  # 只测试一个避免太慢
            print(f"\n  🎭 测试{personality}人格...")
            result = quick_generate(test_question, personality)
            
            if result and not result.startswith("生成失败"):
                print(f"  📝 {personality}回答: {result[:100]}...")
                print(f"  ✅ {personality}生成测试通过")
            else:
                print(f"  ❌ {personality}生成失败: {result}")
                return False
        
        return True
    except Exception as e:
        print(f"  ❌ 人格化生成测试失败: {e}")
        return False

def test_full_pipeline():
    """测试完整流程"""
    print("\n🧪 测试完整流程...")
    
    try:
        controller = PersonalityController()
        test_question = "如何学习编程？"
        
        result = controller.generate_with_personality(
            test_question, 
            personality="ENTJ",
            num_candidates=2  # 减少候选数量以加快测试
        )
        
        if "error" not in result:
            print(f"  📊 最佳匹配度: {result['best_score']:.3f}")
            print(f"  📝 回答长度: {len(result['best_response'])}字符")
            print("  ✅ 完整流程测试通过")
            return True
        else:
            print(f"  ❌ 完整流程测试失败: {result['error']}")
            return False
    except Exception as e:
        print(f"  ❌ 完整流程测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 MBTI-LLM 集成测试开始")
    print("=" * 50)
    
    tests = [
        ("人格规则库", test_personality_rules),
        ("风格评分器", test_style_scorer),
        ("Ollama连接", test_ollama_connection),
        ("人格化生成", test_personality_generation),
        ("完整流程", test_full_pipeline)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
        else:
            print(f"\n⚠️  {test_name}测试失败，可能影响后续功能")
    
    print("\n" + "=" * 50)
    print(f"📈 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统运行正常")
        print("\n🚀 可以运行 python demo.py 开始使用")
    elif passed >= 2:
        print("⚠️  部分测试通过，基础功能可用")
        print("💡 建议检查Ollama配置后重新测试")
    else:
        print("❌ 多项测试失败，请检查环境配置")
        print("\n🔧 故障排除步骤:")
        print("1. 确保安装了所有依赖: pip install -r requirements.txt")
        print("2. 启动Ollama服务: ollama serve")
        print("3. 下载模型: ollama pull qwen2.5:7b")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  测试中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程异常: {e}")
        sys.exit(1)