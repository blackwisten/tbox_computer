#!/usr/bin/env python3
"""
调试流式调用以查看完整的响应内容
"""

import os
import json
import httpx
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def debug_streaming_call():
    """调试流式调用"""
    print("=== 调试DashScope流式API调用 ===")
    
    # 检查API密钥
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        print("❌ 未找到DASHSCOPE_API_KEY环境变量")
        return
    
    print(f"✅ API密钥已设置: {api_key[:8]}...{api_key[-4:]}")
    
    # 测试模型
    model = "qwen3-32b"
    print(f"🎯 目标模型: {model}")
    
    # 构造测试请求
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-SSE": "enable"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一个专业的计算机硬件配置专家，根据用户的预算和用途，提供最佳的硬件配置建议。请以标准JSON格式返回结果，包含configuration、total_price和recommendation字段。"},
            {"role": "user", "content": json.dumps({
                "budget": 5000,
                "usage": "游戏",
                "config_level": "中端"
            }, ensure_ascii=False)}
        ],
        "temperature": 0.7,
        "stream": True,
        "parameters": {
            "enable_thinking": True
        }
    }
    
    print(f"📤 发送请求到: {url}")
    
    try:
        # 发送流式请求
        content = ""
        line_count = 0
        with httpx.stream("POST", url, headers=headers, json=payload, timeout=30.0) as response:
            print(f"📥 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                # 处理SSE流式响应
                for line in response.iter_lines():
                    line_count += 1
                    print(f"第{line_count}行: {line}")
                    
                    if line.startswith("data:"):
                        data = line[5:].strip()
                        if data and data != "[DONE]":
                            try:
                                chunk = json.loads(data)
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    if "content" in delta and delta["content"] is not None:
                                        content += delta["content"]
                            except json.JSONDecodeError as e:
                                print(f"JSON解析错误: {e}, 数据: {data}")
                                continue
                print(f"✅ 完整响应内容: {content}")
                print(f"✅ 内容长度: {len(content)}")
                
                # 尝试解析JSON
                if content.strip():
                    try:
                        result = json.loads(content)
                        print(f"✅ JSON解析成功: {json.dumps(result, ensure_ascii=False, indent=2)}")
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON解析失败: {e}")
                        print(f"内容预览: {content[:200]}")
                else:
                    print("❌ 响应内容为空")
            else:
                # 读取错误响应
                error_text = response.read()
                print(f"❌ 错误响应: {error_text}")
            
    except Exception as e:
        print(f"💥 请求异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_streaming_call()