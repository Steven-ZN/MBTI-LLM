"""
MBTI-LLM 主程序 - 直接可用版本
"""

from personality_controller import PersonalityController

def main():
    """主函数 - 直接运行MBTI人格化生成"""
    
    # 初始化控制器，使用deepseek-llm:7b模型
    controller = PersonalityController(base_model="deepseek-llm:7b")
    
    print("MBTI-LLM 人格化语言模型")
    print("=" * 40)
    print("支持人格类型: ENTJ | INFP | ISTP")
    print("输入 'quit' 退出")
    print("=" * 40)
    
    while True:
        # 获取用户输入
        question = input("\n请输入您的问题: ").strip()
        
        if question.lower() in ['quit', 'exit', '退出']:
            print("程序结束")
            break
        
        if not question:
            continue
        
        # 选择人格类型
        print("\n选择人格类型:")
        print("1. ENTJ (执行官型 - 权威指导)")
        print("2. INFP (调停者型 - 温暖启发)")
        print("3. ISTP (虚拟家型 - 务实客观)")
        
        choice = input("请选择 (1-3): ").strip()
        
        personality_map = {
            '1': 'ENTJ',
            '2': 'INFP', 
            '3': 'ISTP'
        }
        
        if choice not in personality_map:
            print("无效选择，使用默认ENTJ")
            personality = 'ENTJ'
        else:
            personality = personality_map[choice]
        
        print(f"\n正在生成{personality}风格回答...")
        
        try:
            # 生成回答 - 增加候选数量以充分利用GPU
            result = controller.generate_with_personality(
                question, 
                personality=personality,
                num_candidates=6  # 7B模型支持更多并发
            )
            
            if "error" in result:
                print(f"生成失败: {result['error']}")
                continue
            
            # 显示结果
            print(f"\n【{personality}】人格匹配度: {result['best_score']:.3f}")
            print("-" * 40)
            print(result['best_response'])
            print("-" * 40)
            
        except Exception as e:
            print(f"生成过程出错: {e}")
            print("请检查Ollama服务是否正常运行")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序中断")
    except Exception as e:
        print(f"程序异常: {e}")
        print("请确保:")
        print("1. Ollama服务正在运行 (ollama serve)")
        print("2. gpt-oss:20b模型可用")
        print("3. 安装了必要依赖 (pip install requests jieba)")