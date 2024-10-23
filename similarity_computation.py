"""
一致性计算

该脚本用于计算知识图谱实体标签的一致性。具体功能包括：
- 根据标签对实体进行分组
- 使用预训练的Chinese-BERT模型计算实体名的向量表示
- 计算标签组内实体名的一致性得分
- 将一致性计算结果保存为JSON文件，并保存前10个结果和排序结果

主要函数和变量：
- preprocess_name(): 预处理实体名
- get_word_vector(): 获取词向量
- batch(): 分批处理函数
- compute_and_save_consistency(): 计算一致性并保存结果
- save_top_10_results(): 保存前10个一致性结果
- save_sorted_results(): 保存排序后的一致性结果

使用示例：
```python
if __name__ == "__main__":
    compute_and_save_consistency(label_groups)
"""
import random  # 用于随机抽样
import json  # 用于处理 JSON 数据
from collections import defaultdict  # 用于创建默认字典
from sklearn.metrics.pairwise import cosine_similarity  # 用于计算余弦相似度
import numpy as np  # 用于数值计算
import re  # 用于正则表达式处理
from transformers import BertTokenizer, BertModel  # 用于加载BERT模型和tokenizer
from data_preprocess import knowledge_graph  # 导入知识图谱模块
from tqdm import tqdm  # 用于显示进度条
import os  # 用于文件和目录操作

# 测试数据
entities = knowledge_graph.entities

# 根据标签分组
label_groups = defaultdict(list)
for entity_id, entity in entities.items():
    label_groups[entity['label']].append(entity['name'])


# 预处理函数
def preprocess_name(name):
    """
    预处理实体名：移除特殊字符并转换为小写
    :param name: 实体名
    :return: 预处理后的实体名
    """
    name = re.sub(r'[^\w\s]', '', name)  # 移除特殊字符
    name = name.lower()  # 转为小写
    return name


# 加载预训练的Chinese-BERT模型和tokenizer
model_path = r'G:\pythonProject\Knowledge Graph\webapp\bhlpro\bert-base-chinese'
tokenizer = BertTokenizer.from_pretrained(model_path)
model = BertModel.from_pretrained(model_path)

# 获取词向量
vector_cache = {}


def get_word_vector(word):
    """
    获取词向量，如果词向量已缓存则直接返回缓存结果
    :param word: 单词
    :return: 词向量
    """
    if word in vector_cache:
        return vector_cache[word]
    inputs = tokenizer(word, return_tensors='pt')
    outputs = model(**inputs)
    cls_vector = outputs.last_hidden_state[:, 0, :].detach().numpy()  # 获取[CLS] token的向量表示
    vector_cache[word] = cls_vector
    return cls_vector


# 分批处理
def batch(iterable, n=1):
    """
    分批处理函数
    :param iterable: 可迭代对象
    :param n: 每批次大小
    :return: 分批后的可迭代对象
    """
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


# 计算一致性并逐批保存结果
def compute_and_save_consistency(label_groups, batch_size=1, output_file='Data/similarity/all_consistency_results.json'):
    """
    计算一致性并逐批保存结果
    :param label_groups: 标签分组
    :param batch_size: 每批次处理大小
    :param output_file: 输出文件路径
    """
    # 创建进度文件夹
    progress_directory = 'Data/similarity/'
    if not os.path.exists(progress_directory):
        os.makedirs(progress_directory)

    all_results = {}
    batch_counter = 0
    total_batches = len(label_groups)

    with tqdm(total=total_batches, desc="Processing", unit="batch") as pbar:
        for label, names in label_groups.items():
            if len(names) > 1:
                if len(names) > 10:
                    names = random.sample(names, 10)
                preprocessed_names = [preprocess_name(name) for name in names if name.strip()]
                preprocessed_names = [name for name in preprocessed_names if name]
                if preprocessed_names:
                    vectors = []
                    for name_batch in batch(preprocessed_names, batch_size):
                        batch_vectors = [get_word_vector(name) for name in name_batch]
                        vectors.extend(batch_vectors)
                    if vectors:
                        vectors = np.vstack(vectors)
                        similarities = cosine_similarity(vectors)
                        np.fill_diagonal(similarities, 0)
                        avg_similarity = similarities.sum() / (len(preprocessed_names) * (len(preprocessed_names) - 1))
                        if avg_similarity > 0:
                            all_results[label] = {
                                "consistency_score": avg_similarity,
                                "names": names
                            }
            batch_counter += 1
            pbar.update(1)
            # 保存进度到文件
            with open(os.path.join(progress_directory, 'progress.json'), 'w', encoding='utf-8') as f:
                json.dump({"progress": batch_counter / total_batches * 100}, f)
            if batch_counter % batch_size == 0:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(all_results, f, ensure_ascii=False, indent=4)
                save_top_10_results(all_results)
                save_sorted_results(all_results)
                print(f"Results up to batch {batch_counter} saved to {output_file}")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=4)
        save_top_10_results(all_results)
        save_sorted_results(all_results)
        print(f"All results saved to {output_file}")


def save_top_10_results(all_results):
    """
    保存前10个一致性结果
    :param all_results: 所有一致性结果
    """
    top_10_results = dict(sorted(all_results.items(), key=lambda item: item[1]['consistency_score'], reverse=True)[:10])
    with open('Data/similarity/top_10_results.json', 'w', encoding='utf-8') as f:
        json.dump(top_10_results, f, ensure_ascii=False, indent=4)


def save_sorted_results(all_results):
    """
    保存排序后的一致性结果
    :param all_results: 所有一致性结果
    """
    sorted_results = dict(sorted(all_results.items(), key=lambda item: item[1]['consistency_score'], reverse=True))
    with open('Data/similarity/sorted_results.json', 'w', encoding='utf-8') as f:
        json.dump(sorted_results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    compute_and_save_consistency(label_groups)
