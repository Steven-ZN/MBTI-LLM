"""
快速设置脚本
自动检查和配置MBTI-LLM运行环境
"""

import subprocess
import sys
import requests
import time

def check_python_version():
    """检查Python版本"""
    print("🐍 检查Python版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro} - 版本兼容")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor}.{version.micro} - 需要Python 3.8+")
        return False

def install_dependencies():
    """安装Python依赖"""
    print("\n📦 安装Python依赖...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        print("  ✅ Python依赖安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ 依赖安装失败: {e.stderr}")
        return False

def check_ollama():
    """检查Ollama安装和服务状态"""
    print("\n🤖 检查Ollama状态...")
    
    # 检查Ollama是否安装
    try:
        result = subprocess.run(["ollama", "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"  ✅ Ollama已安装: {result.stdout.strip()}")
        else:
            print("  ❌ Ollama未安装")
            print("  💡 请访问 https://ollama.ai 下载安装")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("  ❌ Ollama未安装或不在PATH中")
        print("  💡 请访问 https://ollama.ai 下载安装")
        return False
    
    # 检查服务状态
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("  ✅ Ollama服务运行正常")
            return True
        else:
            print("  ⚠️  Ollama服务异常")
            return False
    except requests.exceptions.RequestException:
        print("  ⚠️  Ollama服务未启动")
        print("  💡 请运行: ollama serve")
        return False

def check_model():
    """检查推荐模型是否已下载"""
    print("\n📥 检查模型状态...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model["name"] for model in models]
            
            recommended_models = ["gpt-oss:20b", "gpt-oss:latest", "qwen2.5:7b"]
            found_model = None
            
            for model in recommended_models:
                if any(model in name for name in model_names):
                    found_model = model
                    break
            
            if found_model:
                print(f"  ✅ 找到推荐模型: {found_model}")
                return True
            else:
                print("  ⚠️  未找到推荐模型")
                print("  💡 建议下载: ollama pull gpt-oss:20b")
                return False
        else:
            print("  ❌ 无法获取模型列表")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ 检查模型失败: {e}")
        return False

def download_model():
    """下载推荐模型"""
    print("\n⬇️  下载推荐模型...")
    try:
        print("  📡 开始下载 gpt-oss:20b (这可能需要几分钟)...")
        result = subprocess.run(["ollama", "pull", "gpt-oss:20b"], 
                              capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            print("  ✅ 模型下载成功")
            return True
        else:
            print(f"  ❌ 模型下载失败: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("  ⏰ 下载超时，请手动执行: ollama pull gpt-oss:20b")
        return False
    except Exception as e:
        print(f"  ❌ 下载过程出错: {e}")
        return False

def run_test():
    """运行集成测试"""
    print("\n🧪 运行集成测试...")
    try:
        result = subprocess.run([sys.executable, "test_integration.py"], 
                              capture_output=True, text=True, timeout=120)
        print(result.stdout)
        if result.stderr:
            print("错误输出:", result.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("  ⏰ 测试超时")
        return False
    except Exception as e:
        print(f"  ❌ 测试执行失败: {e}")
        return False

def main():
    """主设置流程"""
    print("🚀 MBTI-LLM 环境设置向导")
    print("=" * 50)
    
    steps = [
        ("Python版本", check_python_version, None, True),
        ("安装依赖", install_dependencies, None, True),
        ("Ollama状态", check_ollama, None, True),
        ("模型检查", check_model, download_model, False),
        ("集成测试", run_test, None, False)
    ]
    
    all_success = True
    
    for step_name, check_func, fix_func, required in steps:
        success = check_func()
        
        if not success:
            if fix_func:
                user_input = input(f"\n❓ {step_name}有问题，是否尝试自动修复? (y/n): ").strip().lower()
                if user_input == 'y':
                    success = fix_func()
                
            if not success and required:
                print(f"\n❌ 必需的{step_name}设置失败，无法继续")
                all_success = False
                break
            elif not success:
                print(f"\n⚠️  {step_name}设置失败，但不影响基本功能")
                all_success = False
    
    print("\n" + "=" * 50)
    if all_success:
        print("🎉 环境设置完成！所有组件正常运行")
        print("\n🚀 现在可以运行:")
        print("  python demo.py     # 启动演示程序")
        print("  python test_integration.py  # 运行测试")
    else:
        print("⚠️  环境设置部分完成，建议查看上述信息")
        print("\n🔧 手动设置步骤:")
        print("1. 安装Ollama: https://ollama.ai")
        print("2. 启动服务: ollama serve")
        print("3. 下载模型: ollama pull gpt-oss:20b")
        print("4. 运行测试: python test_integration.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  设置中断")
    except Exception as e:
        print(f"\n❌ 设置过程异常: {e}")