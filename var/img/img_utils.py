# -*- coding: utf-8 -*-

import os
import random
from flask import current_app


def get_image_types():
    """
    获取所有图片类型
    """
    image_base = current_app.config["IMAGE_BASE"]
    types = []
    for item in os.listdir(image_base):
        if os.path.isdir(os.path.join(image_base, item)):
            types.append(item)
    return sorted(types)


def get_random_image_path(img_type, orientation=None):
    """
    获取随机图片路径

    Args:
        img_type (str): 图片类型
        orientation (str): 可选，'horizontal'或'vertical'
    """
    image_base = current_app.config["IMAGE_BASE"]
    allowed_extensions = current_app.config["ALLOWED_EXTENSIONS"]

    # 验证图片类型
    if img_type not in get_image_types():
        return None

    # 验证orientation参数
    valid_orientations = ["horizontal", "vertical"]
    if orientation and orientation not in valid_orientations:
        return None

    # 如果没有指定方向，随机选择
    if not orientation:
        orientation = random.choice(valid_orientations)

    # 构建完整路径
    type_dir = os.path.join(image_base, img_type, orientation)

    # 检查目录是否存在
    if not os.path.exists(type_dir):
        # 如果指定方向不存在，尝试另一个方向
        if orientation == "horizontal":
            fallback_orientation = "vertical"
        else:
            fallback_orientation = "horizontal"

        type_dir = os.path.join(image_base, img_type, fallback_orientation)
        if not os.path.exists(type_dir):
            return None

        orientation = fallback_orientation

    # 获取该目录下所有图片
    images = []
    for file in os.listdir(type_dir):
        if os.path.isfile(os.path.join(type_dir, file)):
            ext = file.split(".")[-1].lower()
            if ext in allowed_extensions:
                images.append(file)

    if not images:
        return None

    # 随机选择一张图片
    selected_image = random.choice(images)
    return os.path.join(type_dir, selected_image), orientation


def get_images_info(img_type, base_url=""):
    """
    获取指定类型的图片信息

    Args:
        img_type (str): 图片类型
        base_url (str): 基础URL, 用于构建绝对路径
    """
    image_base = current_app.config["IMAGE_BASE"]
    allowed_extensions = current_app.config["ALLOWED_EXTENSIONS"]

    images = {"horizontal": [], "vertical": []}
    for orientation in ["horizontal", "vertical"]:
        type_dir = os.path.join(image_base, img_type, orientation)
        if not os.path.exists(type_dir):
            continue

        for file in os.listdir(type_dir):
            file_path = os.path.join(type_dir, file)
            if os.path.isfile(file_path):
                ext = file.split(".")[-1].lower()
                if ext in allowed_extensions:
                    # 使用基础URL构建绝对路径
                    absolute_path = (
                        f"{base_url}/image/{img_type}/{orientation}/{file}"
                        if base_url
                        else f"/image/{img_type}/{orientation}/{file}"
                    )

                    images[orientation].append(
                        {
                            "filename": file,
                            "path": absolute_path,
                            "size": os.path.getsize(file_path),
                        }
                    )
    return images


def get_all_image_types_count():
    """
    获取所有类型的图片数量统计
    """
    # image_base = current_app.config['IMAGE_BASE']
    types = get_image_types()

    total_count = 0
    type_counts = {}

    for img_type in types:
        info = get_images_info(img_type)
        type_count = len(info["horizontal"]) + len(info["vertical"])
        type_counts[img_type] = type_count
        total_count += type_count

    return {"types": type_counts, "count": total_count}
