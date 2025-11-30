import json
import random
import os

def add_prices_to_json(file_path):
    """
    为硬件数据添加价格信息
    """
    # 读取JSON文件
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 为每个项目添加价格
    for item in data:
        # 如果价格为null，则生成一个随机价格
        if item.get('price') is None:
            # 根据硬件类型设置价格范围
            if 'cpu' in file_path:
                # CPU价格范围 500-5000元
                item['price'] = round(random.uniform(500, 5000), 2)
            elif 'motherboard' in file_path:
                # 主板价格范围 300-3000元
                item['price'] = round(random.uniform(300, 3000), 2)
            elif 'memory' in file_path:
                # 内存价格范围 200-2000元
                item['price'] = round(random.uniform(200, 2000), 2)
            elif 'video-card' in file_path:
                # 显卡价格范围 1000-10000元
                item['price'] = round(random.uniform(1000, 10000), 2)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_dir = os.path.join(current_dir, 'json')
    
    # 处理所有硬件数据文件
    for filename in os.listdir(json_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(json_dir, filename)
            print(f"处理文件: {file_path}")
            add_prices_to_json(file_path)
    
    print("价格数据添加完成!")

if __name__ == "__main__":
    main()
# 此文件已被弃用，我们不再需要随机生成价格数据
# 硬件价格应该通过大模型查询实时数据或者从电商平台API获取
