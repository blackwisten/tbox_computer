"""配置结果渲染工具"""

from jinja2 import Template
import os
from typing import Optional


def render_configuration_html(configuration: dict, budget: int, usage: str, config_level: str, compatibility_result: Optional[dict] = None) -> str:
    """
    将配置结果渲染为HTML
    
    Args:
        configuration: 配置信息字典
        budget: 预算
        usage: 用途
        config_level: 配置级别
        compatibility_result: 兼容性检查结果
        
    Returns:
        HTML字符串
    """
    # 创建模板目录（如果不存在）
    template_dir = "template"
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
    
    # 创建输出目录（如果不存在）
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 检查是否有错误信息
    if "error" in configuration:
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>计算机配置生成失败</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .error {{ color: red; }}
        .recommendation {{ background-color: #fff3cd; padding: 15px; border-radius: 5px; margin-top: 20px; }}
    </style>
</head>
<body>
    <h1>计算机配置生成失败</h1>
    <p class="error">{configuration['error']}</p>
    <div class="recommendation">
        <h3>建议：</h3>
        <p>如果您有其他预算考虑或其他需求，请重新提交配置请求。</p>
    </div>
    <p><strong>预算:</strong> ¥{budget}</p>
    <p><strong>用途:</strong> {usage}</p>
    <p><strong>配置级别:</strong> {config_level}</p>
</body>
</html>
        """
    else:
        # 正常配置结果
        # 构建兼容性警告HTML
        compatibility_html = ""
        if compatibility_result and not compatibility_result.get("compatible", True):
            compatibility_html = """
    <div class="compatibility-issues" style="background-color: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px; margin-top: 20px; border: 1px solid #f5c6cb;">
        <h3>兼容性问题警告</h3>
        <ul>
"""
            for issue in compatibility_result.get("issues", []):
                compatibility_html += f"            <li>{issue}</li>\n"
            compatibility_html += "        </ul>\n"
            
            # 添加建议解决方案
            compatibility_html += "        <p><strong>建议解决方案：</strong></p>\n"
            compatibility_html += "        <ul>\n"
            
            # 根据问题类型提供解决方案
            issues = compatibility_result.get("issues", [])
            if any("插槽不兼容" in issue for issue in issues):
                compatibility_html += "            <li>请更换与CPU插槽兼容的主板</li>\n"
            if any("内存不兼容" in issue for issue in issues):
                compatibility_html += "            <li>请选择与主板支持的内存类型匹配的内存条</li>\n"
                
            compatibility_html += "        </ul>\n"
            compatibility_html += "    </div>\n"
        
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>计算机配置推荐</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .config-item {{ margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .config-name {{ font-weight: bold; color: #333; }}
        .config-reason {{ color: #7f8c8d; font-style: italic; }}
        .recommendation {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; }}
        .budget-analysis {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin-top: 20px; }}
        .taobao-link {{ display: inline-block; margin-top: 10px; padding: 5px 10px; background-color: #ff5000; color: white; text-decoration: none; border-radius: 3px; }}
        .taobao-link:hover {{ background-color: #e54500; }}
    </style>
</head>
<body>
    <h1>计算机配置推荐</h1>
    <p><strong>预算:</strong> ¥{budget}</p>
    <p><strong>用途:</strong> {usage}</p>
    <p><strong>配置级别:</strong> {config_level}</p>
    
    <div class="config-item">
        <div class="config-name">CPU: {configuration['configuration']['cpu']['name']}</div>
        <div class="config-reason">推荐理由: {configuration['configuration']['cpu']['reason']}</div>
        <a href="{configuration['configuration']['cpu'].get('link', '#')}" class="taobao-link" target="_blank">在淘宝上查看</a>
    </div>
    
    <div class="config-item">
        <div class="config-name">主板: {configuration['configuration']['motherboard']['name']}</div>
        <div class="config-reason">推荐理由: {configuration['configuration']['motherboard']['reason']}</div>
        <a href="{configuration['configuration']['motherboard'].get('link', '#')}" class="taobao-link" target="_blank">在淘宝上查看</a>
    </div>
    
    <div class="config-item">
        <div class="config-name">内存: {configuration['configuration']['memory']['name']}</div>
        <div class="config-reason">推荐理由: {configuration['configuration']['memory']['reason']}</div>
        <a href="{configuration['configuration']['memory'].get('link', '#')}" class="taobao-link" target="_blank">在淘宝上查看</a>
    </div>
    
    <div class="config-item">
        <div class="config-name">显卡: {configuration['configuration']['video-card']['name']}</div>
        <div class="config-reason">推荐理由: {configuration['configuration']['video-card']['reason']}</div>
        <a href="{configuration['configuration']['video-card'].get('link', '#')}" class="taobao-link" target="_blank">在淘宝上查看</a>
    </div>
    
    {compatibility_html}
    
    <div class="budget-analysis">
        <h3>预算分析:</h3>
        <p>该配置符合{config_level}定位，适合{usage}使用场景。</p>
    </div>
    
    <div class="recommendation">
        <h3>配置建议:</h3>
        <p>{configuration['recommendation']}</p>
    </div>
</body>
</html>
        """
    
    # 写入输出文件
    output_file = "output/output_config.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return html_content

def render_template(template_str: str, **kwargs) -> str:
    """
    使用Jinja2模板引擎渲染模板
    
    Args:
        template_str: 模板字符串
        **kwargs: 模板变量
        
    Returns:
        渲染后的字符串
    """
    template = Template(template_str)
    return template.render(**kwargs)
