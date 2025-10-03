#!/usr/bin/env python3
"""
简单功能测试 - 测试基本配置和初始化
"""

import os


def test_basic_imports():
    """测试基本导入功能"""
    print("🔍 测试基本导入...")

    try:
        from vllm_mcp.models import MultimodalRequest, TextContent
        from vllm_mcp.providers.dashscope_provider import DashscopeProvider
        from vllm_mcp.server import MultimodalMCPServer
        print("✅ 所有模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False


def test_server_initialization():
    """测试服务器初始化"""
    print("\n🔍 测试服务器初始化...")

    try:
        from vllm_mcp.server import MultimodalMCPServer

        server = MultimodalMCPServer()
        print(f"✅ 服务器初始化成功")
        print(f"   配置的提供商数量: {len(server.config.get('providers', []))}")
        print(f"   已初始化的提供商: {list(server.providers.keys())}")

        if 'dashscope' in server.providers:
            provider = server.providers['dashscope']
            print(f"   Dashscope 支持的模型数: {len(provider.supported_models)}")
            print(f"   默认模型: qwen-vl-plus")

        return True
    except Exception as e:
        print(f"❌ 服务器初始化失败: {e}")
        return False


def test_environment_config():
    """测试环境配置"""
    print("\n🔍 测试环境配置...")

    # 检查环境变量
    dashscope_key = os.getenv("DASHSCOPE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    print(f"   DASHSCOPE_API_KEY: {'✅ 已设置' if dashscope_key else '⚠️  未设置'}")
    print(f"   OPENAI_API_KEY: {'✅ 已设置' if openai_key else '⚠️  未设置'}")

    if dashscope_key:
        print("   ✅ Dashscope 配置正常，可以测试模型")
        return True
    else:
        print("   ⚠️  需要 Dashscope API 密钥才能测试模型")
        return False


def test_configuration_file():
    """测试配置文件"""
    print("\n🔍 测试配置文件...")

    try:
        if os.path.exists("config.json"):
            import json
            with open("config.json", 'r') as f:
                config = json.load(f)

            print(f"✅ 配置文件加载成功")
            print(f"   传输方式: {config.get('transport', 'stdio')}")
            print(f"   主机: {config.get('host', 'localhost')}")
            print(f"   端口: {config.get('port', 8080)}")
            print(f"   提供商配置: {len(config.get('providers', []))}")

            return True
        else:
            print("⚠️  config.json 文件不存在")
            return False
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        return False


def test_startup_script():
    """测试启动脚本"""
    print("\n🔍 测试启动脚本...")

    scripts = ["scripts/start.sh", "scripts/start-dev.sh"]

    for script in scripts:
        if os.path.exists(script) and os.access(script, os.X_OK):
            print(f"   ✅ {script} 存在且可执行")
        else:
            print(f"   ❌ {script} 不存在或不可执行")
            return False

    return True


def test_examples():
    """测试示例文件"""
    print("\n🔍 测试示例文件...")

    examples = [
        "examples/client_example.py",
        "examples/list_models.py",
        "examples/mcp_client_config.json"
    ]

    for example in examples:
        if os.path.exists(example):
            print(f"   ✅ {example} 存在")
        else:
            print(f"   ❌ {example} 不存在")
            return False

    return True


def main():
    """运行所有测试"""
    print("🚀 VLLM MCP Server 简单功能测试")
    print("=" * 50)

    tests = [
        ("基本导入", test_basic_imports),
        ("服务器初始化", test_server_initialization),
        ("环境配置", test_environment_config),
        ("配置文件", test_configuration_file),
        ("启动脚本", test_startup_script),
        ("示例文件", test_examples),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results[test_name] = False

    # 测试结果汇总
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")

    print(f"\n总体结果: {passed}/{total} 测试通过")

    if passed >= 5:  # 至少 5/6 通过
        print("🎉 基本功能测试通过！项目结构正常。")
        print("\n🚀 推荐使用步骤:")
        print("   1. 确保 .env 文件中有正确的 API 密钥")
        print("   2. 启动服务器: ./scripts/start.sh")
        print("   3. 查看模型列表: uv run python examples/list_models.py")

        if os.getenv("DASHSCOPE_API_KEY"):
            print("   4. 测试文本生成（已配置 Dashscope）")

        return True
    else:
        print("⚠️  部分测试失败，请检查项目配置。")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)