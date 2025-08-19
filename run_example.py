"""
运行示例 - 展示MBTI人格化效果
"""

from personality_controller import PersonalityController

def run_example():
    """运行一个完整的示例"""
    
    print("MBTI-LLM 人格化示例")
    print("=" * 40)
    
    # 初始化控制器
    controller = PersonalityController(base_model="gpt-oss:20b")
    
    # 测试问题
    question = "如何提高学习效率？"
    print(f"问题: {question}")
    print()
    
    # 测试三种人格类型
    personalities = ["ENTJ", "INFP", "ISTP"]
    
    for personality in personalities:
        print(f"【{personality}】人格回答:")
        print("-" * 30)
        
        try:
            result = controller.generate_with_personality(
                question, 
                personality=personality,
                num_candidates=2  # 减少候选数量以加快速度
            )
            
            if "error" not in result:
                print(f"人格匹配度: {result['best_score']:.3f}")
                print(f"回答: {result['best_response']}")
            else:
                print(f"生成失败: {result['error']}")
                
        except Exception as e:
            print(f"出错: {e}")
        
        print("-" * 30)
        print()

if __name__ == "__main__":
    run_example()