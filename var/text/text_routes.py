# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, current_app
from . import text_utils as utils

bp = Blueprint('text_routes', __name__)

@bp.route('/api/text/types')
def get_text_types_api():
    return jsonify({
        'types': utils.get_text_types(),
        'count': len(utils.get_text_types())
    })

@bp.route('/api/text/<text_type>/count')
def get_text_count_api(text_type):
    count = utils.get_text_count_by_type(text_type)
    # 检查类型是否存在
    if count == 0 and text_type not in utils.get_text_types():
        return jsonify({
            'error': 'Invalid text type',
            'type': text_type
        }), 404
    
    return jsonify({
        'count': count,
        'type': text_type
    })

@bp.route('/api/text/count')
def get_all_text_types_count_api():
    count_data = utils.get_all_text_types_count()
    return jsonify(count_data)

@bp.route('/random_text/<text_type>')
def get_random_text_api(text_type):
    random_text = utils.get_random_text_by_type(text_type)
    # 检查类型是否存在以及是否有文本
    if random_text is None:
        # 检查是否是类型不存在
        if text_type not in utils.get_text_types():
            return jsonify({
                'error': 'Invalid text type',
                'type': text_type
            }), 404
        else:
            # 类型存在但没有文本文件或文本文件为空
            return jsonify({
                'error': 'No text available',
                'type': text_type
            }), 404
    
    return jsonify({
        'type': text_type,
        'text': random_text
    })