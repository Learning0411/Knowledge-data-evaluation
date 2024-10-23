"""
度数统计与保存脚本

该脚本用于计算知识图谱中实体的度数，并将计算结果保存为JSON文件。具体功能包括：
- 计算每个实体的度数
- 将度数统计结果按顺序保存为JSON文件
- 使用进度条显示计算和保存过程

主要函数和变量：
- calculate_and_save_degree_counts(): 计算度数并保存结果
- progress: 全局变量，用于跟踪计算进度

使用示例：
```python
if __name__ == '__main__':
    calculate_and_save_degree_counts()
"""

import json # 用于处理 JSON 数据
import os # 用于文件和目录操作
import data_preprocess # 导入数据预处理模块
from tqdm import tqdm # 用于显示进度条

progress = {
    'current': 0,
    'total': 0
}


def calculate_and_save_degree_counts():
    """
    计算知识图谱中每个实体的度数，并将结果保存为 JSON 文件
    """
    global progress

    # 计算度数
    degree_count = data_preprocess.knowledge_graph.calculate_degree_count()
    sorted_degree_count = dict(sorted(degree_count.items()))

    # 更新进度
    total_progress = len(degree_count)
    progress['total'] = total_progress
    progress['current'] = 0  # 确保从0开始

    # 将结果存入 JSON 文件
    output_file = 'Data/degree/degree_counts.json'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with tqdm(total=total_progress, desc="计算并保存度数", unit="item") as pbar:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sorted_degree_count, f, ensure_ascii=False, indent=4)
            for i in range(total_progress):
                progress['current'] = i + 1
                pbar.update(1)

    progress['current'] = total_progress

    print("成功保存文件到", output_file)


if __name__ == '__main__':
    calculate_and_save_degree_counts()