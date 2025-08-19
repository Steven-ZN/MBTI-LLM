"""
高性能版本 - 最大化GPU利用率
"""

from personality_controller import PersonalityController
import time

def high_performance_demo():
    """高性能演示 - 大量并发生成"""
    
    print("高性能MBTI-LLM演示 - 最大化GPU利用率")
    print("=" * 50)
    
    controller = PersonalityController(base_model="deepseek-llm:7b")
    
    question = "如何在现代社会中保持竞争力？"
    print(f"问题: {question}")
    print()
    
    # 大量并发生成测试
    num_candidates = 12  # 大幅增加候选数量
    print(f"正在并行生成 {num_candidates} 个候选回答...")
    
    start_time = time.time()
    
    try:
        result = controller.generate_with_personality(
            question,
            personality="ENTJ", 
            num_candidates=num_candidates,
            return_all=True  # 返回所有候选以查看效果
        )
        
        end_time = time.time()
        
        if "error" not in result:
            print(f"生成完成!")
            print(f"耗时: {end_time - start_time:.2f}秒")
            print(f"成功生成: {result['candidates_count']} 个候选")
            print(f"最佳匹配度: {result['best_score']:.3f}")
            print()
            print("最佳回答:")
            print("-" * 40)
            print(result['best_response'])
            print("-" * 40)
            print()
            
            # 显示所有候选的评分
            if result.get('all_candidates'):
                print("所有候选评分:")
                for i, (candidate, score) in enumerate(result['all_candidates'][:5], 1):
                    print(f"{i}. 评分: {score:.3f} - {candidate[:50]}...")
                    
        else:
            print(f"❌ 生成失败: {result['error']}")
            
    except Exception as e:
        print(f"❌ 执行失败: {e}")

def stress_test():
    """压力测试 - 连续高并发"""
    
    print("\n🔥 压力测试 - 连续高并发生成")
    print("=" * 50)
    
    controller = PersonalityController(base_model="deepseek-llm:7b")
    
    questions = [
        "什么是人工智能？",
        "如何提高工作效率？", 
        "未来科技的发展趋势是什么？",
        "如何培养创新思维？"
    ]
    
    total_start = time.time()
    
    for i, question in enumerate(questions, 1):
        print(f"\n第{i}轮: {question}")
        
        start_time = time.time()
        try:
            result = controller.generate_with_personality(
                question,
                personality=["ENTJ", "INFP", "ISTP"][i % 3],  # 轮换人格
                num_candidates=10,  # 每次10个候选
            )
            end_time = time.time()
            
            if "error" not in result:
                print(f"✅ 耗时: {end_time - start_time:.2f}秒 | 评分: {result['best_score']:.3f}")
            else:
                print(f"❌ 失败: {result['error']}")
                
        except Exception as e:
            print(f"❌ 异常: {e}")
    
    total_end = time.time()
    print(f"\n📊 压力测试完成，总耗时: {total_end - total_start:.2f}秒")

if __name__ == "__main__":
    print("选择测试模式:")
    print("1. 高性能演示 (大量并发)")
    print("2. 压力测试 (连续高并发)")
    
    choice = input("请选择 (1-2): ").strip()
    
    if choice == "1":
        high_performance_demo()
    elif choice == "2":
        stress_test()
    else:
        print("无效选择，运行高性能演示")
        high_performance_demo()