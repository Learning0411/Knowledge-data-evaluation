"""
标签统计脚本

该脚本用于统计知识图谱中实体标签的数量，并将统计结果保存为JSON文件。具体功能包括：
- 通过滑动窗口逐批处理三元组
- 统计每批三元组中实体标签的数量
- 将统计结果按批次保存为JSON文件

主要函数和变量：
- get_label(entity_name, entities): 获取实体的标签
- count_labels_in_batch(batch, entities): 统计批次中的标签数量
- sliding_window_triplets(triplets, window_size): 生成滑动窗口的三元组批次
- save_to_json(file_path, data): 将数据保存为JSON文件
- main(): 主函数，执行统计和保存操作
- progress: 全局变量，用于跟踪计算进度

使用示例：
```python
if __name__ == '__main__':
    main()
"""

import json # 用于处理 JSON 数据
import data_preprocess # 导入数据预处理模块
import os # 用于文件和目录操作
from tqdm import tqdm # 用于显示进度条

progress = 0


def get_label(entity_name, entities):
    """
    获取实体的标签
    参数：
    - entity_name: 实体名称
    - entities: 实体字典

    返回：
    - 实体的标签，如果找不到则返回 None
    """
    for entity_id, entity_info in entities.items():
        if entity_info['name'] == entity_name:
            return entity_info['label']
    return None


def count_labels_in_batch(batch, entities):
    """
    统计批次中的标签数量
    参数：
    - batch: 三元组批次
    - entities: 实体字典

    返回：
    - 不同标签的数量
    """
    label_counts = {}
    for a, r, b in batch:
        a_label = get_label(a, entities)
        b_label = get_label(b, entities)

        if a_label:
            if a_label not in label_counts:
                label_counts[a_label] = 0
            label_counts[a_label] += 1

        if b_label:
            if b_label not in label_counts:
                label_counts[b_label] = 0
            label_counts[b_label] += 1
    return len(label_counts)  # 统计不同标签的数量


def sliding_window_triplets(triplets, window_size):
    """
    生成滑动窗口的三元组批次
    参数：
    - triplets: 三元组列表
    - window_size: 窗口大小

    生成：
    - 每次生成一个窗口大小的三元组批次
    """
    for i in range(0, len(triplets), window_size):
        yield triplets[i:i + window_size]


def save_to_json(file_path, data):
    """
    将数据保存为JSON文件
    参数：
    - file_path: 文件路径
    - data: 要保存的数据
    """
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + '\n')


def main():
    """
    主函数，执行统计和保存操作
    """
    global progress
    triplets = data_preprocess.knowledge_graph.relationships
    entities = data_preprocess.knowledge_graph.entities
    window_size = 100
    output_file = 'Data/relevance/label_counts.json'

    # 确保目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # 清空之前的记录
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('')

    total_batches = (len(triplets) + window_size - 1) // window_size

    with tqdm(total=total_batches, desc="计算统计数据", unit="batch") as pbar:
        for i, batch in enumerate(sliding_window_triplets(triplets, window_size)):
            label_count = count_labels_in_batch(batch, entities)
            batch_result = {
                'batch_number': i + 1,
                'label_count': label_count
            }
            save_to_json(output_file, batch_result)
            pbar.update(1)
            progress = (i + 1) / total_batches * 100


if __name__ == '__main__':
    main()
