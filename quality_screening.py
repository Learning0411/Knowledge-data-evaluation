import re
from collections import defaultdict
import os
from tqdm import tqdm
import json
import data_preprocess

progress = {
    "current": 0,
    "total": 0
}

# 检查符号是否成对出现
def has_unpaired_symbols(s, symbol_pairs):
    stack = []
    for char in s:
        if char in symbol_pairs:
            stack.append(char)
        elif char in symbol_pairs.values():
            if not stack or stack.pop() != char:
                return True
    return bool(stack)

# 定义符号对
symbol_pairs = { '〈': '〉', '{': '}', '[': ']', '(': ')' }

# 筛选低质量三元组并统计各类别数量
def filter_low_quality_triples(triples):
    low_quality_triples = {
        '不规范实体关系': [],
        '异常符号匹配': [],
        '低质量头实体': [],
        '不完备三元组': [],
        '低质量关系': []
    }

    low_quality_counts = {
        '不规范实体关系': 0,
        '异常符号匹配': 0,
        '低质量头实体': 0,
        '不完备三元组': 0,
        '低质量关系': 0
    }

    progress["total"] = len(triples)

    for i, (s, p, o) in enumerate(tqdm(triples, desc="Filtering triples")):
        # 更新当前进度
        progress["current"] = i + 1

        # 规则1：检查三元组是否完整
        if not s or not p or not o:
            low_quality_triples['不完备三元组'].append((s, p, o))
            low_quality_counts['不完备三元组'] += 1
            continue

        # 规则3：实体中的符号需要成对出现
        if has_unpaired_symbols(s, symbol_pairs) or has_unpaired_symbols(o, symbol_pairs):
            low_quality_triples['异常符号匹配'].append((s, p, o))
            low_quality_counts['异常符号匹配'] += 1

        # 规则4：头实体长度在2到10字符之间
        if not (2 <= len(s)):
            low_quality_triples['低质量头实体'].append((s, p, o))
            low_quality_counts['低质量头实体'] += 1

        # 规则6：关系不能有标点符号
        if re.search(r'[^\w\s]', p):
            low_quality_triples['低质量关系'].append((s, p, o))
            low_quality_counts['低质量关系'] += 1

        # 规则2：头实体和关系不能有英文或纯数字，尾实体不能有特殊符号（允许《》）
        if re.search(r'[a-zA-Z]', s) or re.match(r'^\d+$', s) or re.search(r'[a-zA-Z]', p) or re.match(r'^\d+$',p) or re.search(r'[^a-zA-Z0-9\u4e00-\u9fff《》]', o):
            low_quality_triples['不规范实体关系'].append((s, p, o))
            low_quality_counts['不规范实体关系'] += 1

    return low_quality_triples, low_quality_counts

def main():
    # 示例数据
    triples = data_preprocess.knowledge_graph.relationships

    # 筛选低质量三元组并获取详细信息和统计数据
    low_quality_triples, low_quality_counts = filter_low_quality_triples(triples)

    # 检查目录是否存在，不存在则创建
    output_dir = './Data/low_quality_triples'
    os.makedirs(output_dir, exist_ok=True)

    # 保存低质量三元组详细信息到JSON文件
    json_file_path = os.path.join(output_dir, "low_quality_triples.json")
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(low_quality_triples, json_file, ensure_ascii=False, indent=4)
        print(f"JSON file saved: {json_file_path}")

    # 保存低质量三元组统计数据到JSON文件
    json_counts_file_path = os.path.join(output_dir, "low_quality_counts.json")
    with open(json_counts_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(low_quality_counts, json_file, ensure_ascii=False, indent=4)
        print(f"JSON file saved: {json_counts_file_path}")

if __name__ == '__main__':
    main()
