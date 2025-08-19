"""
MBTI-LLM 项目展示脚本
快速演示系统核心功能
"""

from personality_controller import PersonalityController

def showcase_demo():
    """展示项目核心功能"""
    
    print("🎭 MBTI-LLM 零训练人格化系统")
    print("=" * 50)
    print("GitHub: https://github.com/Steven-ZN/MBTI-LLM")
    print("=" * 50)
    
    # 初始化控制器
    controller = PersonalityController(base_model="deepseek-llm:7b")
    
    # 测试问题
    question = "在AI时代，程序员应该如何保持竞争力？"
    print(f"🤔 测试问题: {question}\n")
    
    personalities = [
        ("ENTJ", "执行官型 - 权威指导"),
        ("INFP", "调停者型 - 温暖启发"), 
        ("ISTP", "虚拟家型 - 务实客观")
    ]
    
    print("🎯 三种人格风格对比:")
    print("-" * 50)
    
    for personality, description in personalities:
        print(f"\n【{personality}】{description}")
        print("⏳ 生成中...")
        
        try:
            result = controller.generate_with_personality(
                question,
                personality=personality,
                num_candidates=4
            )
            
            if "error" not in result:
                print(f"✅ 匹配度: {result['best_score']:.3f}")
                print(f"📝 回答: {result['best_response']}")
            else:
                print(f"❌ 生成失败: {result['error']}")
                
        except Exception as e:
            print(f"❌ 异常: {e}")
        
        print("-" * 50)
    
    print("\n🎉 展示完成！")
    print("💡 更多功能:")
    print("  - python main.py (交互式使用)")
    print("  - python high_performance.py (性能测试)")
    print("  - python setup.py (环境配置)")

if __name__ == "__main__":
    showcase_demo()