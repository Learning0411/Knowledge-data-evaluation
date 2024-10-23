"""
知识图谱构建和分析模块

该模块提供了一组工具类，用于构建和分析知识图谱。具体功能包括：
- 加载实体和三元组数据
- 计算实体和关系的数量
- 计算实体标签的数量和类型
- 计算实体度分布和关系密度
- 获取常见实体和关系
- 计算连通分量数量

主要类和方法：
- KnowledgeGraph 类：用于构建和分析知识图谱
  - add_entity(entity_id, name, label): 添加一个实体到知识图谱中
  - add_triplet(entity1, relationship, entity2): 添加一个三元组到知识图谱中
  - load_entities(file_path): 从 CSV 文件中加载实体数据
  - load_triplets(file_path): 从 CSV 文件中加载三元组数据
  - calculate_entity_count(): 计算实体的数量
  - calculate_relationship_count(): 计算关系的数量
  - calculate_triplet_count(): 计算三元组的数量
  - calculate_relationship_type_count(): 计算关系类型的数量
  - calculate_entity_label_counts(): 计算每个标签的实体数量
  - calculate_entity_label_types_count(): 计算标签类型的数量
  - calculate_entity_degree_distribution(): 计算实体的度分布
  - calculate_entity_relationship_density(): 计算实体关系密度
  - top_entities(top_n=100): 获取前 N 个常见实体
  - top_relationships(top_n=15): 获取前 N 个常见关系
  - calculate_degree_count(): 计算每个度数的实体数量
  - top_entity_labels(top_n=10): 获取前 N 个常见实体标签
  - top_entities_with_triplets(top_n=10): 获取前 N 个具有三元组的实体
  - calculate_connected_components(): 计算连通分量的数量

使用示例：
```python
# 创建 KnowledgeGraph 实例并加载数据
knowledge_graph = KnowledgeGraph()

# 加载实体和三元组数据
knowledge_graph.load_entities('path_to_entities_file.csv')
knowledge_graph.load_triplets('path_to_triplets_file.csv')

# 获取实体和关系的数量
entity_count = knowledge_graph.calculate_entity_count()
relationship_count = knowledge_graph.calculate_relationship_count()

# 获取前 10 个常见实体
top_entities = knowledge_graph.top_entities(10)
"""

import csv
from collections import Counter
import networkx as nx


class KnowledgeGraph:
    def __init__(self):
        # 初始化实体和关系
        self.entities = {}
        self.relationships = []

    def add_entity(self, entity_id, name, label):
        """
            添加一个实体到知识图谱中

            :param entity_id: 实体的唯一标识
            :param name: 实体的名称
            :param label: 实体的标签
        """
        self.entities[entity_id] = {'name': name, 'label': label}

    def add_triplet(self, entity1, relationship, entity2):
        """
            添加一个三元组到知识图谱中

            :param entity1: 头实体的唯一标识
            :param relationship: 关系类型
            :param entity2: 尾实体的唯一标识
        """
        self.relationships.append((entity1, relationship, entity2))

    def load_entities(self, file_path):
        """
            从 CSV 文件中加载实体数据

            :param file_path: CSV 文件的路径
        """
        with open(file_path, 'r', encoding='utf-8-sig') as f:  # 处理 BOM
            reader = csv.DictReader(f)
            for row in reader:
                entity_id = row['id']
                name = row['name']
                label = row['label']
                self.add_entity(entity_id, name, label)

    def load_triplets(self, file_path):
        """
            从 CSV 文件中加载三元组数据

            :param file_path: CSV 文件的路径
        """
        with open(file_path, 'r', encoding='utf-8-sig') as f:  # 处理 BOM
            reader = csv.DictReader(f)
            for row in reader:
                entity1 = row['头实体']
                relationship = row['关系']
                entity2 = row['尾实体']
                self.add_triplet(entity1, relationship, entity2)

    def calculate_entity_count(self):
        """
            计算实体的数量

            :return: 实体数量
        """
        return len(self.entities)

    def calculate_relationship_count(self):
        """
            计算关系的数量

            :return: 关系数量
        """
        return len(self.relationships)

    def calculate_triplet_count(self):
        """
            计算三元组的数量

            :return: 三元组数量
        """
        return len(self.relationships)

    def calculate_relationship_type_count(self):
        """
            计算关系类型的数量

            :return: 关系类型数量
        """
        relationship_types = set([rel[1] for rel in self.relationships])
        return len(relationship_types)

    def calculate_entity_label_counts(self):
        """
            计算每个标签的实体数量

            :return: 标签计数器
        """
        labels = [entity['label'] for entity in self.entities.values()]
        return Counter(labels)

    def calculate_entity_label_types_count(self):
        """
            计算标签类型的数量

            :return: 标签类型数量
        """
        label_counts = self.calculate_entity_label_counts()
        return len(label_counts)

    def calculate_entity_degree_distribution(self):
        """
            计算实体的度分布

            :return: 度分布字典
        """
        degrees = Counter([rel[0] for rel in self.relationships] + [rel[2] for rel in self.relationships])
        sorted_degrees = dict(sorted(degrees.items(), key=lambda item: item[1], reverse=True))
        return sorted_degrees

    def calculate_entity_relationship_density(self):
        """
            计算实体关系密度

            :return: 实体关系密度
        """
        if self.calculate_entity_count() == 0:
            return 0
        return round(self.calculate_relationship_count() / self.calculate_entity_count(), 2)

    def top_entities(self, top_n=100):
        """
            获取前 N 个常见实体

            :param top_n: 要获取的实体数量
            :return: 前 N 个常见实体
        """
        entity_counts = Counter([rel[0] for rel in self.relationships] + [rel[2] for rel in self.relationships])
        return entity_counts.most_common(top_n)

    def top_relationships(self, top_n=15):
        """
            获取前 N 个常见关系

            :param top_n: 要获取的关系数量
            :return: 前 N 个常见关系
        """
        relationship_counts = Counter([rel[1] for rel in self.relationships])
        return relationship_counts.most_common(top_n)

    def calculate_degree_count(self):
        """
            计算每个度数的实体数量

            :return: 度数计数字典
        """
        degree_count = Counter(self.calculate_entity_degree_distribution().values())
        # 将结果转换为字典
        degree_count_dict = dict(degree_count)
        return degree_count_dict

    def top_entity_labels(self, top_n=10):
        """
            获取前 N 个常见实体标签

            :param top_n: 要获取的标签数量
            :return: 前 N 个常见标签
        """
        label_counts = self.calculate_entity_label_counts()
        return label_counts.most_common(top_n)

    def top_entities_with_triplets(self, top_n=10):
        """
           获取前 N 个具有三元组的实体

           :param top_n: 要获取的实体数量
           :return: 前 N 个具有三元组的实体及其三元组
        """
        entity_counts = Counter([rel[0] for rel in self.relationships] + [rel[2] for rel in self.relationships])
        top_entities = entity_counts.most_common(top_n)
        top_entities_with_triplets = []

        for entity, count in top_entities:
            entity_triplets = []
            for rel in self.relationships:
                if entity in rel:
                    entity_triplets.append(rel)
            top_entities_with_triplets.append((entity, count, entity_triplets))

        return top_entities_with_triplets

    def calculate_connected_components(self):
        """
            计算连通分量的数量

            :return: 连通分量的数量
        """
        graph = nx.DiGraph()
        for entity in self.entities:
            graph.add_node(entity)
        for s, p, o in self.relationships:
            graph.add_edge(s, o, relationship=p)

        return nx.number_weakly_connected_components(graph)


# 创建 KnowledgeGraph 实例并加载数据
knowledge_graph = KnowledgeGraph()

# 加载实体和三元组数据
knowledge_graph.load_entities(r'Data\entities_file.csv')
knowledge_graph.load_triplets(r'Data\triples_file.csv')



