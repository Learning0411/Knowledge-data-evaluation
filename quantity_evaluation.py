"""
质量报告生成脚本

该脚本用于生成知识图谱的质量报告。具体功能包括：
- 计算知识图谱的统计数据，例如三元组数量、实体数量、关系种类数量等
- 生成质量报告并将其保存为 JSON 文件

主要函数和变量：
- main(): 主函数，执行各项任务并生成质量报告
- progress: 全局变量，用于跟踪进度

使用示例：
```python
if __name__ == "__main__":
    main()
"""

import json  # 用于处理 JSON 数据
from tqdm import tqdm  # 用于显示进度条
from data_preprocess import knowledge_graph  # 导入知识图谱模块
import time  # 用于模拟计算时间
progress = 0


def main():
    global progress
    # 定义需要执行的任务，每个任务包含任务名称和对应的函数
    tasks = [
        ("三元组数量 (Triplet Count)", knowledge_graph.calculate_triplet_count),
        ("实体数量 (Entity Count)", knowledge_graph.calculate_entity_count),
        ("关系种类数量 (Relationship Type Count)", knowledge_graph.calculate_relationship_type_count),
        ("实体种类数量 (Entity Label Types Count)", knowledge_graph.calculate_entity_label_types_count),
        ("实体关系密度 (Entity-Relationship Density)", knowledge_graph.calculate_entity_relationship_density),
        ("连通度数量 (Connected Components Count)", knowledge_graph.calculate_connected_components),
        ("出现次数最多的前100个实体及其出现次数 (Most Frequent Entities)", lambda: knowledge_graph.top_entities(top_n=100)),
        ("出现次数最多的前15个关系及其出现次数 (Most Frequent Relationships)", lambda: knowledge_graph.top_relationships(top_n=15)),
        ("出现次数最多的前15个实体 (Top 15 Entity Labels)", lambda: knowledge_graph.top_entity_labels(top_n=15))
    ]

    quality_report = {}

    # 使用tqdm创建进度条
    with tqdm(total=len(tasks), desc="计算统计数据", unit="task") as pbar:
        for i, (task_name, task_func) in enumerate(tasks):
            quality_report[task_name] = task_func()
            pbar.update(1)
            progress = (i + 1) / len(tasks) * 100
            time.sleep(1)  # 模拟计算任务的时间

    for key, value in quality_report.items():
        print(f"{key}: {value}")

    # 将质量报告保存为 JSON 文件
    output_file_path = 'Data/quality_report.json'
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(quality_report, f, ensure_ascii=False, indent=4)
    print(f"质量报告已保存到 {output_file_path}")

    return quality_report

if __name__ == "__main__":
    main()
