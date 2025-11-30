"""计算机配置核心逻辑"""

import json
import os
import random
import logging
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from config import my_model, my_system_prompt_config_tips
from fastmcp import FastMCP
import httpx

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def query_llm_for_configuration(budget: float, usage: str, config_level: str) -> Dict[str, Any]:
    """
    使用大模型查询计算机配置
    
    Args:
        budget: 预算
        usage: 用途
        config_level: 配置级别
        
    Returns:
        配置信息字典
    """
    try:
        logger.info(f"正在调用大模型生成配置: budget={budget}, usage={usage}, config_level={config_level}")
        
        # 检查API密钥是否已设置
        api_key = os.getenv('DASHSCOPE_API_KEY')
        if not api_key:
            logger.warning("未找到DASHSCOPE_API_KEY环境变量")
            # 返回模拟配置数据
            return get_mock_configuration(budget, usage, config_level)
        
        logger.info(f"API密钥已设置: {api_key[:8]}...{api_key[-4:]}")
        
        # 构造输入参数
        input_data = {
            "budget": budget,
            "usage": usage,
            "config_level": config_level
        }
        
        logger.info(f"发送请求到模型: {my_model}")
        
        # 直接调用DashScope API（使用流式调用）
        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-DashScope-SSE": "enable"
        }
        
        # 移除response_format参数以兼容enable_thinking=true
        payload = {
            "model": my_model,
            "messages": [
                {"role": "system", "content": my_system_prompt_config_tips},
                {"role": "user", "content": json.dumps(input_data, ensure_ascii=False)}
            ],
            "temperature": 0.7,
            "stream": True,
            "parameters": {
                "enable_thinking": True
            }
        }
        
        logger.info(f"请求载荷: {json.dumps(payload, ensure_ascii=False)[:200]}...")
        
        # 发送HTTP流式请求
        content = ""
        with httpx.stream("POST", url, headers=headers, json=payload, timeout=60.0) as response:
            if response.status_code != 200:
                error_text = response.read()
                logger.warning(f"大模型调用失败，状态码: {response.status_code}")
                logger.warning(f"错误响应内容: {error_text}")
                logger.warning(f"请求头: {dict(headers)}")
                # 返回模拟数据
                return get_mock_configuration(budget, usage, config_level)
            
            # 处理SSE流式响应
            for line in response.iter_lines():
                if line.startswith("data:"):
                    data = line[5:].strip()
                    if data and data != "[DONE]":
                        try:
                            chunk = json.loads(data)
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta and delta["content"] is not None:
                                    content += delta["content"]
                        except json.JSONDecodeError:
                            # 如果解析失败，可能是非JSON数据，跳过
                            continue
        
        logger.info("成功收到来自大模型的流式响应")
        logger.info(f"完整响应内容长度: {len(content)}")
        logger.debug(f"完整响应内容: {content}")
        
        # 检查内容是否为空
        if not content or not content.strip():
            logger.warning("大模型返回空内容")
            # 返回模拟数据
            return get_mock_configuration(budget, usage, config_level)
        
        # 清理响应内容，移除可能的Markdown代码块标记
        cleaned_content = content.strip()
        if cleaned_content.startswith("```json"):
            cleaned_content = cleaned_content[7:]  # 移除开头的 ```json
        if cleaned_content.endswith("```"):
            cleaned_content = cleaned_content[:-3]  # 移除结尾的 ```
        cleaned_content = cleaned_content.strip()
        
        # 尝试解析JSON
        try:
            result_data = json.loads(cleaned_content)
            logger.info("成功解析大模型响应")
            return result_data
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {str(e)}")
            logger.error(f"清理后的内容前200字符: {cleaned_content[:200] if cleaned_content else '空内容'}")
            # 返回模拟数据
            return get_mock_configuration(budget, usage, config_level)
        
    except Exception as e:
        logger.error(f"查询大模型时出错: {str(e)}", exc_info=True)
        # 出错时返回模拟配置数据
        return get_mock_configuration(budget, usage, config_level)

def get_mock_configuration(budget: float, usage: str, config_level: str) -> Dict[str, Any]:
    """
    获取模拟配置数据
    
    Args:
        budget: 预算
        usage: 用途
        config_level: 配置级别
        
    Returns:
        模拟配置信息字典
    """
    logger.info("使用模拟配置数据")
    
    # 根据预算和用途生成模拟配置
    if budget < 4000:
        # 入门级配置
        configuration = {
            "cpu": {
                "name": "AMD Ryzen 5 3500X",
                "price": 800,
                "reason": "性价比较高的6核处理器，适合日常办公和轻度游戏"
            },
            "motherboard": {
                "name": "ASRock 880GM-LE FX",
                "price": 400,
                "reason": "支持AMD处理器，具备基本功能，价格实惠"
            },
            "memory": {
                "name": "Crucial CP2K64G56C46U5 128 GB",
                "price": 300,
                "reason": "大容量内存，满足多任务处理需求"
            },
            "video_card": {
                "name": "PNY VCQP600-PB",
                "price": 1200,
                "reason": "专业级显卡，适合入门级游戏和图形处理"
            }
        }
        total_price = sum(item["price"] for item in configuration.values())
        recommendation = f"这是一套入门级配置，适合{usage}使用。总价格约为¥{total_price}。"
    elif budget < 7000:
        # 中端配置
        configuration = {
            "cpu": {
                "name": "AMD Ryzen 5 7600X3D",
                "price": 1800,
                "reason": "专为游戏优化的处理器，具备出色的性能表现"
            },
            "motherboard": {
                "name": "MSI Z97-G45 Gaming",
                "price": 800,
                "reason": "游戏主板，具备良好的扩展性和稳定性"
            },
            "memory": {
                "name": "G.Skill Ripjaws S5 32 GB",
                "price": 600,
                "reason": "高速大容量内存，满足游戏和多任务处理需求"
            },
            "video_card": {
                "name": "Gigabyte Vision OC",
                "price": 3500,
                "reason": "中高端显卡，适合1080p和1440p游戏"
            }
        }
        total_price = sum(item["price"] for item in configuration.values())
        recommendation = f"这是一套中端配置，适合{usage}使用。总价格约为¥{total_price}。"
    else:
        # 高端配置
        configuration = {
            "cpu": {
                "name": "AMD Ryzen 5 3500X",
                "price": 900,
                "reason": "高性能处理器，适合专业设计和重度游戏"
            },
            "motherboard": {
                "name": "Biostar B650MT-E PRO",
                "price": 700,
                "reason": "高端主板，支持最新技术，扩展性极佳"
            },
            "memory": {
                "name": "Crucial CP2K64G56C46U5 128 GB",
                "price": 400,
                "reason": "超大容量高速内存，满足专业应用需求"
            },
            "video_card": {
                "name": "MSI GAMING TRIO",
                "price": 5500,
                "reason": "旗舰级显卡，适合4K游戏和专业图形处理"
            }
        }
        total_price = sum(item["price"] for item in configuration.values())
        recommendation = f"这是一套高端配置，适合{usage}使用。总价格约为¥{total_price}。"
    
    return {
        "configuration": configuration,
        "total_price": total_price,
        "recommendation": recommendation
    }

def generate_taobao_link(hardware_name: str, hardware_type: str) -> str:
    """
    为硬件生成淘宝搜索链接
    
    Args:
        hardware_name: 硬件名称
        hardware_type: 硬件类型
        
    Returns:
        淘宝搜索链接
    """
    # 移除可能干扰搜索的特殊字符
    keywords = hardware_name.replace("/", " ").replace("-", " ")
    # 根据硬件类型添加相关关键词
    if hardware_type == "cpu":
        keywords += " CPU处理器"
    elif hardware_type == "motherboard":
        keywords += " 主板"
    elif hardware_type == "memory":
        keywords += " 内存条"
    elif hardware_type == "video-card":
        keywords += " 显卡"
    
    # 生成淘宝搜索链接
    return f"https://s.taobao.com/search?q={keywords}"

def check_compatibility(configuration: dict) -> dict:
    """检查配置中硬件的兼容性"""
    try:
        issues = []
        warnings = []
        
        # 获取配置中的硬件信息
        cpu = configuration.get("cpu", {})
        motherboard = configuration.get("motherboard", {})
        memory = configuration.get("memory", {})
        video_card = configuration.get("video-card", {})
        power_supply = configuration.get("power-supply", {})
        case = configuration.get("case", {})
        
        # CPU与主板兼容性检查
        cpu_name = cpu.get("name", "").lower()
        cpu_socket = cpu.get("socket", "")
        motherboard_socket = motherboard.get("socket", "")
        
        # 建立CPU-主板兼容性映射规则
        compatibility_rules = {
            # AMD CPU 插槽规则
            "am4": ["am4", "b350", "b450", "x370", "x470", "x570"],
            "am5": ["am5", "b650", "x670"],
            "trx4": ["trx4", "wrx40"],
            # Intel CPU 插槽规则
            "lga1151": ["lga1151", "h110", "b150", "z170", "h170", "q170", "q150"],
            "lga1155": ["lga1155", "h61", "b65", "p67", "z68", "h67"],
            "lga1150": ["lga1150", "h81", "b85", "z87", "h87", "q87", "q85"],
            "lga1200": ["lga1200", "h410", "b460", "z490", "h470"],
            "lga1700": ["lga1700", "b560", "z590", "h510", "h570", "z690", "b660", "h610", "z790"],
            "lga2066": ["lga2066", "x299"],
        }
        
        # 检查CPU和主板插槽是否匹配
        if cpu_socket and motherboard_socket:
            # 转换为小写进行比较
            cpu_socket_lower = cpu_socket.lower()
            motherboard_socket_lower = motherboard_socket.lower()
            
            # 检查是否在同一插槽家族
            is_compatible = False
            for cpu_family, compatible_sockets in compatibility_rules.items():
                if cpu_socket_lower.startswith(cpu_family) or cpu_socket_lower in compatible_sockets:
                    if motherboard_socket_lower in compatible_sockets:
                        is_compatible = True
                        break
            
            # 如果没有找到匹配规则，则进行直接比较
            if not is_compatible and cpu_socket_lower != motherboard_socket_lower:
                issues.append(f"CPU与主板插槽不兼容：CPU插槽为{cpu_socket}，主板插槽为{motherboard_socket}")
        
        # 品牌交叉检查
        if ("intel" in cpu_name and "amd" in motherboard_socket.lower()) or \
           ("amd" in cpu_name and "intel" in motherboard_socket.lower()):
            issues.append("CPU与主板品牌不兼容：AMD CPU不能安装在Intel主板上，反之亦然")
        
        # 内存类型兼容性检查
        memory_type = memory.get("type", "")
        motherboard_memory_support = motherboard.get("memory_support", "")
        
        # 特殊处理：如果未提供内存类型，则尝试从内存名称推断
        if not memory_type:
            memory_name = memory.get("name", "").lower()
            if "ddr5" in memory_name:
                memory_type = "DDR5"
            elif "ddr4" in memory_name:
                memory_type = "DDR4"
            elif "ddr3" in memory_name:
                memory_type = "DDR3"
        
        # 特殊处理：如果未提供主板内存支持信息，则尝试从主板名称推断
        if not motherboard_memory_support:
            motherboard_name = motherboard.get("name", "").lower()
            if "b650" in motherboard_name or "x670" in motherboard_name or "am5" in motherboard_name:
                motherboard_memory_support = "DDR5"
            elif "b450" in motherboard_name or "x470" in motherboard_name or "b550" in motherboard_name or "x570" in motherboard_name:
                motherboard_memory_support = "DDR4"
            elif "z87" in motherboard_name or "h81" in motherboard_name or "b85" in motherboard_name:
                motherboard_memory_support = "DDR3"
        
        # 检查内存与主板兼容性
        if memory_type and motherboard_memory_support:
            # 确保类型匹配
            if isinstance(motherboard_memory_support, str):
                if memory_type.upper() not in motherboard_memory_support.upper():
                    issues.append(f"内存不兼容：主板仅支持{motherboard_memory_support}，但配置了{memory_type}内存")
            elif isinstance(motherboard_memory_support, list):
                if not any(memory_type.upper() in support.upper() for support in motherboard_memory_support):
                    issues.append(f"内存不兼容：主板不支持{memory_type}类型的内存")
        
        # 电源功率检查
        total_power_consumption = 0
        if cpu.get("tdp"):
            total_power_consumption += cpu["tdp"]
        if video_card.get("tdp"):
            total_power_consumption += video_card["tdp"]
        # 添加其他组件的功耗估算
        
        psu_power = power_supply.get("power", 0)
        if psu_power > 0 and total_power_consumption > psu_power * 0.8:
            warnings.append(f"电源功率可能不足：估算总功耗{total_power_consumption}W，建议电源功率至少为{int(total_power_consumption/0.8)}W")
        
        # 机箱尺寸兼容性检查
        case_form_factor = case.get("form_factor", "")
        motherboard_form_factor = motherboard.get("form_factor", "")
        
        # 简化的机箱兼容性规则
        form_factor_hierarchy = {
            "Mini ITX": 1,
            "Micro ATX": 2,
            "ATX": 3,
            "EATX": 4,
            "XL ATX": 5
        }
        
        if case_form_factor in form_factor_hierarchy and motherboard_form_factor in form_factor_hierarchy:
            if form_factor_hierarchy[case_form_factor] < form_factor_hierarchy[motherboard_form_factor]:
                issues.append(f"机箱尺寸不兼容：{case_form_factor}机箱无法容纳{motherboard_form_factor}主板")
        
        # 显卡长度兼容性检查
        case_max_gpu_length = case.get("max_gpu_length", 0)
        gpu_length = video_card.get("length", 0)
        
        if case_max_gpu_length > 0 and gpu_length > 0 and gpu_length > case_max_gpu_length:
            issues.append(f"显卡长度不兼容：显卡长度{gpu_length}mm超过机箱支持的最大长度{case_max_gpu_length}mm")
        
        return {
            "compatible": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    except Exception as e:
        return {
            "compatible": False,
            "issues": [f"兼容性检查时出错: {str(e)}"],
            "warnings": []
        }

def estimate_performance(configuration: dict, scenarios: Optional[List[str]] = None) -> dict:
    """估算配置在不同场景下的性能表现"""
    if scenarios is None:
        scenarios = ["办公软件", "网页浏览", "1080p游戏", "1440p游戏", "4k游戏", "视频编辑"]
    
    try:
        # 获取配置中的关键硬件
        cpu = configuration.get("cpu", {})
        memory = configuration.get("memory", {})
        video_card = configuration.get("video-card", {})
        
        # 更复杂的性能评分系统
        performance_scores = {}
        
        # 基于CPU核心数、基础频率和微架构进行评分
        cpu_score = 0
        cpu_cores = cpu.get("core_count", 4)
        cpu_base_clock = cpu.get("base_clock", 3.0)
        cpu_boost_clock = cpu.get("boost_clock", cpu_base_clock)
        cpu_microarchitecture = cpu.get("microarchitecture", "")
        
        # CPU评分基础公式
        cpu_score = cpu_cores * ((cpu_base_clock + cpu_boost_clock) / 2) * 10
        
        # 根据微架构调整评分（较新的架构得分更高）
        microarch_multiplier = 1.0
        if "Zen" in cpu_microarchitecture or "Skylake" in cpu_microarchitecture:
            microarch_multiplier = 1.2
        elif "Piledriver" in cpu_microarchitecture or "Ivy Bridge" in cpu_microarchitecture:
            microarch_multiplier = 0.9
        elif "K10" in cpu_microarchitecture or "Core" in cpu_microarchitecture:
            microarch_multiplier = 0.7
            
        cpu_score *= microarch_multiplier
        
        # 基于内存容量、频率和模块数进行评分
        memory_score = 0
        memory_capacity = memory.get("capacity", memory.get("modules", [0])[0] if memory.get("modules") else 8)
        memory_frequency = memory.get("frequency", 3200)
        
        # 内存评分公式
        memory_score = (memory_capacity / 8) * (memory_frequency / 3200) * 100
        
        # 基于显卡芯片组、显存和频率评分
        gpu_score = 0
        gpu_vram = video_card.get("vram", video_card.get("memory", 6))
        gpu_core_clock = video_card.get("core_clock", 1500)
        gpu_boost_clock = video_card.get("boost_clock", gpu_core_clock)
        gpu_chipset = video_card.get("chipset", "")
        
        # 显卡评分基础公式
        gpu_score = (gpu_vram / 6) * ((gpu_core_clock + gpu_boost_clock) / 2 / 1000) * 200
        
        # 根据显卡系列调整评分
        gpu_multiplier = 1.0
        if "RTX 40" in gpu_chipset:
            gpu_multiplier = 1.5
        elif "RTX 30" in gpu_chipset or "RX 7" in gpu_chipset:
            gpu_multiplier = 1.3
        elif "RTX 20" in gpu_chipset or "RX 6" in gpu_chipset:
            gpu_multiplier = 1.1
        elif "GTX 10" in gpu_chipset or "RX 5" in gpu_chipset:
            gpu_multiplier = 0.8
        elif "GTX 9" in gpu_chipset or "R9" in gpu_chipset:
            gpu_multiplier = 0.6
            
        gpu_score *= gpu_multiplier
        
        # 为每个场景评估性能
        for scenario in scenarios:
            if scenario == "办公软件":
                score = (cpu_score * 0.6 + memory_score * 0.4) / 10
                performance_scores[scenario] = {
                    "score": min(100, round(score)),
                    "recommendation": "流畅" if score > 50 else "一般" if score > 30 else "卡顿"
                }
            elif scenario == "网页浏览":
                score = (cpu_score * 0.3 + memory_score * 0.7) / 10
                performance_scores[scenario] = {
                    "score": min(100, round(score)),
                    "recommendation": "流畅" if score > 60 else "一般" if score > 40 else "卡顿"
                }
            elif scenario == "1080p游戏":
                score = (cpu_score * 0.3 + gpu_score * 0.7) / 20
                performance_scores[scenario] = {
                    "score": min(100, round(score)),
                    "recommendation": "高画质流畅" if score > 80 else "中画质流畅" if score > 60 else "低画质" if score > 40 else "卡顿"
                }
            elif scenario == "1440p游戏":
                score = (cpu_score * 0.3 + gpu_score * 0.7) / 25
                performance_scores[scenario] = {
                    "score": min(100, round(score)),
                    "recommendation": "高画质流畅" if score > 80 else "中画质流畅" if score > 60 else "低画质" if score > 40 else "卡顿"
                }
            elif scenario == "4k游戏":
                score = (cpu_score * 0.3 + gpu_score * 0.7) / 35
                performance_scores[scenario] = {
                    "score": min(100, round(score)),
                    "recommendation": "高画质流畅" if score > 80 else "中画质流畅" if score > 60 else "低画质" if score > 40 else "卡顿"
                }
            elif scenario == "视频编辑":
                score = (cpu_score * 0.4 + memory_score * 0.3 + gpu_score * 0.3) / 15
                performance_scores[scenario] = {
                    "score": min(100, round(score)),
                    "recommendation": "流畅" if score > 70 else "一般" if score > 50 else "卡顿"
                }
        
        return {
            "performance_scores": performance_scores,
            "overall_rating": sum([v["score"] for v in performance_scores.values()]) // len(performance_scores)
        }
    except Exception as e:
        return {
            "error": f"性能预估时出错: {str(e)}",
            "performance_scores": {},
            "overall_rating": 0
        }

def generate_computer_configuration(budget: float, usage: str, config_level: str) -> Dict[str, Any]:
    """根据预算、用途和配置级别生成计算机配置"""
    
    # 预算合理性检查
    if budget < 1000:
        return {
            "error": "预算过低（低于¥1000），无法配置一台可用的电脑。建议至少准备¥3000以上预算。"
        }
    
    if budget > 50000:
        return {
            "error": "您的预算较高（超过¥50000），建议分阶段采购或联系专业人员定制高端配置。"
        }
    
    # 使用大模型查询配置
    result = query_llm_for_configuration(budget, usage, config_level)
    
    # 如果返回了错误信息，直接返回
    if "error" in result:
        return result
    
    # 处理配置结果，添加淘宝链接
    configuration = result.get("configuration", {})
    
    # 为每个组件添加淘宝链接
    for component_name, component in configuration.items():
        if isinstance(component, dict) and "name" in component:
            # 转换组件名称为链接生成所需的类型
            link_type_map = {
                "cpu": "cpu",
                "motherboard": "motherboard",
                "memory": "memory",
                "video_card": "video-card"
            }
            
            link_type = link_type_map.get(component_name, component_name)
            # 确保link_type不是None，如果是则使用默认值"computer-hardware"
            if link_type is None:
                link_type = "computer-hardware"
            component["link"] = generate_taobao_link(component["name"], link_type)
    
    # 计算总价
    total_price = result.get("total_price", 0)
    
    # 获取推荐理由
    recommendation = result.get("recommendation", f"这是一套{config_level}配置，适合{usage}使用。")
    
    return {
        "configuration": configuration,
        "total_price": total_price,
        "compatibility_score": 100.0,  # 简化的兼容性评分
        "recommendation": recommendation
    }
