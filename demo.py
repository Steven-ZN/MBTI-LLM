"""
MBTI-LLM 演示程序
展示三种人格类型的对比效果
"""

import sys
import time
from personality_controller import PersonalityController
from personality_templates import get_personality_examples
from personality_rules import PREDEFINED_PERSONAS

def print_header():
    """打印程序头部信息"""
    print("=" * 60)
    print("MBTI-LLM 人格化语言模型演示")
    print("=" * 60)
    print("基于重排机制的零训练人格化生成系统")
    print("支持人格类型: ENTJ (执行官) | INFP (调停者) | ISTP (虚拟家)")
    print("=" * 60)
    print()

def test_connection(controller):
    """测试Ollama连接"""
    print("🔗 测试Ollama连接...")
    try:
        # 简单测试调用
        test_result = controller._call_ollama(
            "你是一个测试助手", 
            "请回复'连接成功'", 
            temperature=0.1
        )
        if test_result and "成功" in test_result:
            print("✅ Ollama连接成功!")
            return True
        else:
            print("⚠️  Ollama连接异常，但可以继续尝试")
            return True
    except Exception as e:
        print(f"❌ Ollama连接失败: {e}")
        print("\n请检查:")
        print("1. Ollama是否已启动 (ollama serve)")
        print("2. 模型是否已下载 (ollama pull qwen2.5:7b)")
        print("3. API端点是否正确 (默认: http://localhost:11434)")
        return False

def show_predefined_examples():
    """展示预定义示例"""
    print("📚 预定义示例对比:")
    print("-" * 60)
    
    examples = get_personality_examples()
    topic = examples["topic"]
    
    print(f"问题: {topic}")
    print("\n" + "="*60)
    
    for personality in ["ENTJ", "INFP", "ISTP"]:
        persona_name = PREDEFINED_PERSONAS[personality].mbti
        print(f"\n🎭 【{personality} - {persona_name}】风格回答:")
        print("-" * 40)
        print(examples[f"{personality}_response"])
        print("-" * 40)

def interactive_demo(controller):
    """交互式演示"""
    print("\n🎮 交互式演示:")
    print("输入问题，系统将生成三种人格的回答进行对比")
    print("输入 'quit' 退出，'example' 查看预设示例")
    print("-" * 60)
    
    while True:
        user_input = input("\n💬 请输入您的问题: ").strip()
        
        if user_input.lower() in ['quit', 'exit', '退出']:
            print("👋 感谢使用，再见!")
            break
        
        if user_input.lower() == 'example':
            show_predefined_examples()
            continue
        
        if not user_input:
            print("请输入有效问题")
            continue
        
        print(f"\n🤔 正在生成回答: {user_input}")
        print("=" * 60)
        
        # 为三种人格类型生成回答
        personalities = ["ENTJ", "INFP", "ISTP"]
        
        for i, personality in enumerate(personalities, 1):
            print(f"\n【{i}/3】正在生成 {personality} 风格回答...")
            
            try:
                result = controller.generate_with_personality(
                    user_input, 
                    personality=personality,
                    num_candidates=3
                )
                
                if "error" in result:
                    print(f"❌ {personality} 生成失败: {result['error']}")
                    continue
                
                persona_info = PREDEFINED_PERSONAS[personality]
                print(f"\n🎭 【{personality}】人格特征: {', '.join(['高' + t for t in ['E' if persona_info.e_score > 0 else 'I', 'N' if persona_info.s_score < 0 else 'S', 'T' if persona_info.t_score > 0 else 'F', 'J' if persona_info.j_score > 0 else 'P']])}")
                print(f"💯 匹配度评分: {result['best_score']:.3f}")
                print(f"📝 回答:")
                print("-" * 40)
                print(result['best_response'])
                print("-" * 40)
                
            except Exception as e:
                print(f"❌ {personality} 生成过程出错: {e}")
        
        print("\n" + "="*60)

def analysis_demo(controller):
    """分析演示"""
    print("\n🔍 文本分析演示:")
    print("输入文本，系统将分析其MBTI人格倾向")
    print("-" * 60)
    
    while True:
        text = input("\n📝 请输入要分析的文本 (输入'back'返回): ").strip()
        
        if text.lower() in ['back', '返回']:
            break
        
        if not text:
            print("请输入有效文本")
            continue
        
        print(f"\n🔬 分析文本: {text[:50]}...")
        print("=" * 60)
        
        for personality in ["ENTJ", "INFP", "ISTP"]:
            try:
                analysis = controller.get_analysis(text, personality)
                print(f"\n📊 与{personality}的匹配度: {analysis['overall_score']:.3f}")
                print("详细分析:")
                for metric, score in analysis['breakdown'].items():
                    print(f"  - {metric}: {score:.3f}")
            except Exception as e:
                print(f"❌ {personality}分析出错: {e}")

def main():
    """主函数"""
    print_header()
    
    # 初始化控制器
    print("🚀 初始化人格控制器...")
    try:
        controller = PersonalityController(
            base_model="qwen2.5:7b",
            ollama_url="http://localhost:11434"
        )
        print("✅ 控制器初始化成功!")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return
    
    # 测试连接
    if not test_connection(controller):
        choice = input("\n是否继续运行? (y/n): ").strip().lower()
        if choice != 'y':
            return
    
    # 主菜单循环
    while True:
        print("\n📋 选择功能:")
        print("1. 📚 查看预定义示例对比")
        print("2. 🎮 交互式人格生成演示") 
        print("3. 🔍 文本人格分析演示")
        print("4. 🚪 退出程序")
        
        choice = input("\n请选择 (1-4): ").strip()
        
        if choice == '1':
            show_predefined_examples()
        elif choice == '2':
            interactive_demo(controller)
        elif choice == '3':
            analysis_demo(controller)
        elif choice == '4':
            print("👋 感谢使用，再见!")
            break
        else:
            print("❌ 无效选择，请重新输入")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序已中断，再见!")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        print("请检查依赖安装和Ollama配置")