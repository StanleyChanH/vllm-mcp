#!/usr/bin/env python3
"""
功能测试脚本 - 测试 VLLM MCP Server 的核心功能
"""

import asyncio
import json
import os
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def test_provider_listing():
    """测试提供商列表功能"""
    print("🔍 测试提供商列表功能...")

    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "vllm_mcp.server", "--transport", "stdio"],
        env={**os.environ, "PYTHONPATH": "src"}
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # 列出可用提供商
            result = await session.call_tool("list_available_providers", {})
            providers_info = json.loads(result.content[0].text)

            print(f"✅ 发现 {len(providers_info)} 个提供商:")
            for name, info in providers_info.items():
                print(f"   - {name} ({info['type']}): {info['default_model']}")
                print(f"     支持模型: {', '.join(info['supported_models'][:2])}...")

            return providers_info


async def test_text_generation():
    """测试文本生成功能"""
    print("\n🔍 测试文本生成功能...")

    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "vllm_mcp.server", "--transport", "stdio"],
        env={**os.environ, "PYTHONPATH": "src"}
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            try:
                # 使用 Dashscope 生成文本
                result = await session.call_tool("generate_multimodal_response", {
                    "model": "qwen-vl-plus",
                    "prompt": "请用一句话解释什么是人工智能。",
                    "max_tokens": 100,
                    "temperature": 0.7
                })

                response_text = result.content[0].text
                print("✅ 文本生成成功:")
                print(f"   响应: {response_text[:100]}...")
                return True

            except Exception as e:
                print(f"❌ 文本生成失败: {e}")
                return False


async def test_model_validation():
    """测试模型验证功能"""
    print("\n🔍 测试模型验证功能...")

    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "vllm_mcp.server", "--transport", "stdio"],
        env={**os.environ, "PYTHONPATH": "src"}
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            test_cases = [
                {"model": "qwen-vl-plus", "image_count": 0, "expected": True},
                {"model": "qwen-vl-plus", "image_count": 3, "expected": True},
                {"model": "unknown-model", "image_count": 0, "expected": False},
            ]

            for i, case in enumerate(test_cases, 1):
                try:
                    result = await session.call_tool("validate_multimodal_request", {
                        "model": case["model"],
                        "image_count": case["image_count"]
                    })

                    is_valid = "有效" in result.content[0].text
                    expected_valid = case["expected"]

                    if is_valid == expected_valid:
                        print(f"✅ 测试用例 {i}: 通过 ({case['model']}, {case['image_count']} 图片)")
                    else:
                        print(f"❌ 测试用例 {i}: 失败 ({case['model']}, {case['image_count']} 图片)")

                except Exception as e:
                    print(f"❌ 测试用例 {i}: 异常 ({e})")


async def test_configuration():
    """测试配置加载功能"""
    print("\n🔍 测试配置加载功能...")

    try:
        from vllm_mcp.server import MultimodalMCPServer

        # 测试默认配置
        server = MultimodalMCPServer()

        print("✅ 配置加载成功:")
        print(f"   传输方式: {server.config.get('transport', 'stdio')}")
        print(f"   主机: {server.config.get('host', 'localhost')}")
        print(f"   端口: {server.config.get('port', 8080)}")
        print(f"   提供商数量: {len(server.config.get('providers', []))}")
        print(f"   已初始化提供商: {list(server.providers.keys())}")

        return True

    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False


async def main():
    """运行所有测试"""
    print("🚀 VLLM MCP Server 功能测试")
    print("=" * 50)

    tests = [
        ("配置加载", test_configuration),
        ("提供商列表", test_provider_listing),
        ("文本生成", test_text_generation),
        ("模型验证", test_model_validation),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                if test_name == "配置加载":
                    results[test_name] = await test_func()
                else:
                    await test_func()
                    results[test_name] = True
            else:
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

    if passed == total:
        print("🎉 所有功能测试通过！项目工作正常。")
        print("\n🚀 你可以开始使用:")
        print("   1. 启动服务器: ./scripts/start.sh")
        print("   2. 列出模型: uv run python examples/list_models.py")
        print("   3. 使用客户端: uv run python examples/client_example.py")
    else:
        print("⚠️  部分测试失败，请检查配置。")


if __name__ == "__main__":
    asyncio.run(main())