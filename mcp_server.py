import json
from typing import Optional
from fastmcp import FastMCP
from config import (
    my_model,
    my_template_filename,
    my_output_filename,
    my_system_prompt_config_tips
)
import os
import logging
import json
# 添加dotenv导入以加载环境变量
from dotenv import load_dotenv
# 添加Jinja2相关导入
from jinja2 import Environment, FileSystemLoader
# 导入配置生成功能
from computer_configurator import generate_computer_configuration

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化MCP服务器
mcp = FastMCP("tbox-computer-configurator 🖥️")

@mcp.tool()
async def generate_computer_config(
    budget: int = 5000,
    usage: str = "游戏",
    config_level: str = "中端"
) -> str:
    """
    根据预算和用途生成计算机配置，并提供组装教学指导
    
    Args:
        budget: 预算金额(元)
        usage: 主要用途(如: 游戏, 办公, 设计, 编程等)
        config_level: 配置级别(如: 入门, 中端, 高端)
        
    Returns:
        生成的配置HTML页面，包含配置推荐和组装教学指导
    """
    try:
        logger.info(f"开始生成计算机配置: budget={budget}, usage={usage}, config_level={config_level}")
        
        # 检查API密钥是否已设置
        api_key = os.getenv('DASHSCOPE_API_KEY')
        if not api_key:
            logger.warning("未找到DASHSCOPE_API_KEY环境变量")
            error_html = f"""
            <html>
            <body>
                <h1>配置生成错误</h1>
                <p>未配置API密钥，请检查环境变量设置</p>
            </body>
            </html>
            """
            return error_html
        
        # 生成配置
        configuration_result = generate_computer_configuration(budget, usage, config_level)
        
        # 检查是否有错误
        if "error" in configuration_result:
            logger.error(f"配置生成出错: {configuration_result['error']}")
            error_html = f"""
            <html>
            <body>
                <h1>配置生成错误</h1>
                <p>{configuration_result['error']}</p>
            </body>
            </html>
            """
            return error_html
        
        # 设置Jinja2环境
        env = Environment(loader=FileSystemLoader('template'))
        template = env.get_template(my_template_filename.split('/')[-1])  # 只使用文件名
        
        # 准备模板数据
        template_data = {
            "budget": budget,
            "usage": usage,
            "config_level": config_level,
            "configuration": configuration_result.get("configuration", {}),
            "total_price": configuration_result.get("total_price", 0),
            "recommendation": configuration_result.get("recommendation", ""),
            "compatibility_score": configuration_result.get("compatibility_score", 100)
        }
        
        # 渲染模板
        result = template.render(**template_data)
        
        # 确保输出目录存在
        os.makedirs('output', exist_ok=True)
        
        # 写入输出文件
        output_path = my_output_filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        
        logger.info(f"配置生成完成，已保存到: {output_path}")
        return result
        
    except Exception as e:
        logger.error(f"生成计算机配置时出错: {str(e)}", exc_info=True)
        error_result = f"<html><body><h1>生成配置时出错</h1><p>{str(e)}</p></body></html>"
        return error_result

@mcp.tool()
def get_hardware_info(hardware_type: str, name: str) -> dict:
    """
    获取特定硬件的详细信息
    
    Args:
        hardware_type: 硬件类型(cpu, motherboard, memory, video-card)
        name: 硬件名称
        
    Returns:
        硬件详细信息
    """
    try:
        # 构建文件路径
        file_path = f"json/{hardware_type}.json"
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return {"error": f"硬件类型 {hardware_type} 不存在"}
        
        # 读取JSON文件
        with open(file_path, 'r', encoding='utf-8') as f:
            hardware_data = json.load(f)
        
        # 查找匹配的硬件
        for item in hardware_data:
            if item.get('name') == name:
                return item
        
        return {"error": f"未找到名为 {name} 的 {hardware_type}"}
    except Exception as e:
        return {"error": f"获取硬件信息时出错: {str(e)}"}

@mcp.tool()
def get_assembly_tutorial() -> dict:
    """
    获取电脑组装教程
    
    Returns:
        包含组装步骤和视频教程链接的字典
    """
    tutorial_data = {
        "steps": [
            {
                "step": 1,
                "title": "准备工作",
                "description": "在开始组装前，请确保您有一个干净、宽敞的工作台，并准备好必要的工具，如螺丝刀套装、防静电手环等。"
            },
            {
                "step": 2,
                "title": "安装CPU",
                "description": "首先将CPU正确安装到主板上。注意CPU上的金色小三角标记应与主板插槽上的标记对齐，轻轻放入，不要用力按压。"
            },
            {
                "step": 3,
                "title": "安装散热器",
                "description": "在CPU上均匀涂抹导热硅脂，然后安装散热器。确保散热器牢固固定，并将风扇电源线连接到主板上的CPU_FAN接口。"
            },
            {
                "step": 4,
                "title": "安装内存条",
                "description": "打开内存插槽的卡扣，将内存条对准缺口插入，用力按下直到两侧卡扣自动弹起固定住内存条。"
            },
            {
                "step": 5,
                "title": "安装主板",
                "description": "将主板放入机箱内，对准螺丝孔位，使用铜柱和螺丝将主板固定在机箱上。"
            },
            {
                "step": 6,
                "title": "安装存储设备",
                "description": "将SSD或硬盘安装到机箱相应位置，并用螺丝固定。连接SATA数据线和电源线。"
            },
            {
                "step": 7,
                "title": "安装显卡",
                "description": "将显卡插入主板上的PCI-E插槽，确保完全插入并拧紧螺丝固定。连接显卡所需的电源线。"
            },
            {
                "step": 8,
                "title": "连接线缆",
                "description": "连接主板电源线、CPU电源线、前置面板线（电源开关、重启开关、指示灯等）以及USB和音频线。"
            },
            {
                "step": 9,
                "title": "最终检查",
                "description": "仔细检查所有连接是否牢固，确认无误后可以首次通电开机测试。"
            },
            {
                "step": 10,
                "title": "安装操作系统",
                "description": "制作系统安装盘，设置BIOS从U盘启动，按照提示完成操作系统的安装和驱动程序的更新。"
            }
        ],
        "videos": [
            {
                "title": "电脑组装详细教程视频",
                "url": "https://www.bilibili.com/video/BV1yx411h7uq"
            },
            {
                "title": "电脑配置选购指南",
                "url": "https://www.bilibili.com/video/BV1ih4y1R7GE"
            }
        ]
    }
    
    return tutorial_data

@mcp.tool()
async def compare_configurations(configurations: list) -> str:
    """
    比较多个配置方案
    
    Args:
        configurations: 配置列表，每个配置包含budget, usage, config_level
        
    Returns:
        比较结果的HTML表格
    """
    try:
        # 导入需要的函数
        from computer_configurator import generate_computer_configuration
        
        # 生成各个配置
        config_results = []
        for i, config in enumerate(configurations):
            budget = config.get("budget", 5000)
            usage = config.get("usage", "游戏")
            config_level = config.get("config_level", "中端")
            
            # 生成配置
            configuration = generate_computer_configuration(budget, usage, config_level)
            config_results.append({
                "id": i+1,
                "budget": budget,
                "usage": usage,
                "config_level": config_level,
                "configuration": configuration
            })
        
        # 设置Jinja2环境
        env = Environment(loader=FileSystemLoader('template'))
        template = env.get_template('template_compare.html')
        
        # 渲染模板
        result = template.render(configurations=config_results)
        
        # 确保输出目录存在
        os.makedirs('output', exist_ok=True)
        
        # 写入输出文件
        output_path = 'output/comparison_result.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        
        return result
    except Exception as e:
        error_result = f"<html><body><h1>配置比较时出错</h1><p>{str(e)}</p></body></html>"
        return error_result

@mcp.tool()
def check_compatibility(configuration: dict) -> dict:
    """
    检查配置中硬件的兼容性
    
    Args:
        configuration: 硬件配置字典
        
    Returns:
        兼容性检查结果
    """
    try:
        issues = []
        warnings = []
        
        # 获取配置中的硬件信息
        # 处理两种可能的数据结构
        config_data = configuration.get("configuration", {})
        if not config_data and isinstance(configuration, dict):
            # 如果configuration就是配置数据本身
            config_data = configuration
        
        cpu = config_data.get("cpu", {})
        motherboard = config_data.get("motherboard", {})
        memory = config_data.get("memory", {})
        video_card = config_data.get("video_card", {})
        
        # CPU与主板兼容性检查
        cpu_name = cpu.get("name", "")
        motherboard_socket = motherboard.get("socket", "")
        
        # 简化的兼容性规则（实际应用中需要更复杂的规则）
        if "Intel" in cpu_name and "AMD" in motherboard_socket:
            issues.append("CPU与主板插槽不兼容：Intel CPU不能安装在AMD主板上")
        elif "AMD" in cpu_name and "Intel" in motherboard_socket:
            issues.append("CPU与主板插槽不兼容：AMD CPU不能安装在Intel主板上")
        
        # 内存兼容性检查
        memory_type = memory.get("type", "")
        motherboard_memory_support = motherboard.get("memory_support", "")
        
        if memory_type and motherboard_memory_support:
            if memory_type not in motherboard_memory_support:
                issues.append(f"内存不兼容：主板不支持{memory_type}类型的内存")
        
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

@mcp.tool()
def estimate_performance(configuration: dict, scenarios: Optional[list] = None) -> dict:
    """
    估算配置在不同场景下的性能表现
    
    Args:
        configuration: 硬件配置字典
        scenarios: 场景列表，默认为常见的使用场景
        
    Returns:
        性能预估结果
    """
    if scenarios is None:
        scenarios = ["办公软件", "网页浏览", "1080p游戏", "1440p游戏", "4k游戏", "视频编辑"]
    
    try:
        # 获取配置中的关键硬件
        # 处理两种可能的数据结构
        config_data = configuration.get("configuration", {})
        if not config_data and isinstance(configuration, dict):
            # 如果configuration就是配置数据本身
            config_data = configuration
        
        cpu = config_data.get("cpu", {})
        memory = config_data.get("memory", {})
        video_card = config_data.get("video_card", {})
        
        # 简化的性能评分系统（实际应用中需要更复杂的算法）
        performance_scores = {}
        
        # 基于CPU核心数和基础频率进行简单评分
        cpu_score = 0
        cpu_cores = cpu.get("cores", 4)
        cpu_base_clock = cpu.get("base_clock", 3.0)
        cpu_score = cpu_cores * cpu_base_clock * 10
        
        # 基于内存容量和频率进行评分
        memory_score = 0
        memory_capacity = memory.get("capacity", 8)
        memory_frequency = memory.get("frequency", 3200)
        memory_score = (memory_capacity / 8) * (memory_frequency / 3200) * 100
        
        # 基于显卡VRAM和基础频率评分
        gpu_score = 0
        gpu_vram = video_card.get("vram", 6)
        gpu_base_clock = video_card.get("base_clock", 1500)
        gpu_score = (gpu_vram / 6) * (gpu_base_clock / 1500) * 200
        
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

def main():
    """启动MCP服务器"""
    mcp.run(
        transport="sse",
        host="0.0.0.0",
        port=8000,
        path="/mcp",
        log_level="debug",
    )

if __name__ == "__main__":
    main()