# -*- coding: utf-8 -*-

import os
from flask import current_app

def get_text_types():
    """
    获取所有文本类型
    """
    text_base = current_app.config['TEXT_BASE']
    types = []
    for item in os.listdir(text_base):
        if os.path.isdir(os.path.join(text_base, item)):
            types.append(item)
    return sorted(types)

def get_text_count_by_type(text_type):
    """
    获取指定类型的文本文件统计
    
    Args:
        text_type (str): 文本类型
    
    Returns:
        int: 该类型下的文本文件数量
    """
    text_base = current_app.config['TEXT_BASE']
    type_dir = os.path.join(text_base, text_type)
    
    # 检查类型目录是否存在
    if not os.path.exists(type_dir) or not os.path.isdir(type_dir):
        return 0
    
    # 统计.txt文件数量
    count = 0
    for item in os.listdir(type_dir):
        if os.path.isfile(os.path.join(type_dir, item)) and item.endswith('.txt'):
            count += 1
    
    return count

def get_all_text_types_count():
    """
    获取所有类型的文本文件统计
    
    Returns:
        dict: 包含各类型文本文件数量和总计数量的字典
    """
    text_base = current_app.config['TEXT_BASE']
    types_count = {}
    total_count = 0
    
    # 获取所有文本类型
    types = get_text_types()
    
    # 统计每种类型的文件数量
    for text_type in types:
        count = get_text_count_by_type(text_type)
        types_count[text_type] = count
        total_count += count
    
    return {
        'types': types_count,
        'count': total_count
    }

def get_random_text_by_type(text_type):
    """
    获取指定类型的随机文本
    
    Args:
        text_type (str): 文本类型
    
    Returns:
        str: 随机文本内容
    """
    import random
    
    text_base = current_app.config['TEXT_BASE']
    type_dir = os.path.join(text_base, text_type)
    
    # 检查类型目录是否存在
    if not os.path.exists(type_dir) or not os.path.isdir(type_dir):
        return None
    
    # 获取所有.txt文件
    txt_files = [f for f in os.listdir(type_dir) if f.endswith('.txt')]
    
    # 检查是否有.txt文件
    if not txt_files:
        return None
    
    # 随机选择一个.txt文件
    random_file = random.choice(txt_files)
    file_path = os.path.join(type_dir, random_file)
    
    # 读取文件内容并随机选择一行
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if lines:
            return random.choice(lines).strip()
    
    return None