import json
from flask import Blueprint, render_template, send_from_directory, redirect,jsonify, current_app
import os
import threading
import similarity_computation
import Content_relevance_calculation
import quality_screening
import quantity_evaluation
import ratio
from flask import request, jsonify


triplet_bp = Blueprint('triplet_bp', __name__)


@triplet_bp.route('/')
@triplet_bp.route('/index.html')
def index():
    return render_template('index.html')


@triplet_bp.route('/login.html')
def login():
    return render_template('login.html')


# 数据上传
@triplet_bp.route('/uploading/<file_type>', methods=['POST'])
def upload_file(file_type):
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'Data')
    TRIPLES_FILE_NAME = 'triples_file.csv'
    ENTITIES_FILE_NAME = 'entities_file.csv'

    try:
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
    except Exception as e:
        print(e)
        return jsonify({'message': 'Failed to create upload folder', 'error': str(e)}), 500

    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    try:
        if file_type == 'triples':
            filename = TRIPLES_FILE_NAME
        elif file_type == 'entities':
            filename = ENTITIES_FILE_NAME
        else:
            return jsonify({'message': 'Invalid file type'}), 400

        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        return jsonify({'message': 'File uploaded successfully'})
    except Exception as e:
        print(e)
        return jsonify({'message': 'File upload failed', 'error': str(e)}), 500


# 基于实体关系数量的数据质量评价参数
def Quantity_evaluation():
    result = quantity_evaluation.main()  # 调用主计算函数获取结果
    quantity_evaluation.progress = 100  # 完成后更新进度为100%
    return result


@triplet_bp.route('/start-computation-quantity', methods=['GET'])
def start_computation_quantity():
    threading.Thread(target=Quantity_evaluation).start()
    return jsonify({"status": "Quantity_evaluation started"})


@triplet_bp.route('/get-quantity-progress', methods=['GET'])
def get_quantity_progress():
    return jsonify({"progress": quantity_evaluation.progress}), 200


# 基于实体关系一致性评测
def compute_similarity():
    result = similarity_computation.compute_and_save_consistency(similarity_computation.label_groups)
    return result


@triplet_bp.route('/start-computation-similarity', methods=['GET'])
def start_computation_similarity():
    threading.Thread(target=compute_similarity).start()
    return jsonify({"status": "similarity computation started"})


@triplet_bp.route('/get-similarity-progress', methods=['GET'])
def get_similarity_progress():
    with open('Data/similarity/progress.json', 'r', encoding='utf-8') as f:
        progress_data = json.load(f)
    return jsonify(progress_data)


# 基于实体关系比例
def start_calculation_thread():
    result = ratio.calculate_and_save_degree_counts()  # 调用主计算函数获取结果
    return result


@triplet_bp.route('/start-degree-count-calculation', methods=['GET'])
def start_degree_count_calculation():
    threading.Thread(target=start_calculation_thread).start()
    return jsonify({"status": "degree-count started"})


@triplet_bp.route('/get-degree-count-progress', methods=['GET'])
def get_degree_count_progress():
    return jsonify(ratio.progress), 200


# 基于三元组内容关联度
def compute_relevance():
    result =Content_relevance_calculation.main()
    Content_relevance_calculation.progress = 100  # 完成后更新进度为100%
    return result


@triplet_bp.route('/start-computation-relevance', methods=['GET'])
def start_computation_relevance():
    threading.Thread(target=compute_relevance).start()
    return jsonify({"status": "compute_relevance started"})


@triplet_bp.route('/get-relevance-progress', methods=['GET'])
def get_relevance_progress():
    return jsonify({"progress": Content_relevance_calculation.progress}), 200

# 存量数据质量报告
def Quality_screening_trid():
    quality_screening.main()


@triplet_bp.route('/start-computation-screening', methods=['GET'])
def start_computation_screening():
    threading.Thread(target=Quality_screening_trid).start()
    return jsonify({"status": "Quality_screening started"})


@triplet_bp.route('/get-screening-progress', methods=['GET'])
def get_screening_progress():
    return jsonify(quality_screening.progress), 200


@triplet_bp.route('/results/<filename>', methods=['GET'])
def get_results(filename):
    return send_from_directory('results', filename)