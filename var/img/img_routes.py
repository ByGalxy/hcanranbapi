# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, send_file, redirect, abort, current_app, request
from . import img_utils as utils
from ..toml_config import STWQMC_NAME, STWQMC_VERSION
import os


bp = Blueprint("img_routes", __name__)


@bp.route("/api")
def api_status():
    return jsonify({"status": "OK", "message": STWQMC_NAME, "version": STWQMC_VERSION})


@bp.route("/api/img/types")
def get_image_types_api():
    return jsonify(
        {"types": utils.get_image_types(), "count": len(utils.get_image_types())}
    )


@bp.route("/api/img/count")
def all_image_types_count():
    count_info = utils.get_all_image_types_count()
    return jsonify(count_info)


@bp.route("/api/img/<img_type>/list")
def image_list(img_type):
    if img_type not in utils.get_image_types():
        abort(404, description=f"Invalid image type '{img_type}'")

    base_url = request.host_url.rstrip("/")

    info = utils.get_images_info(img_type, base_url)
    return jsonify({"type": img_type, "images": info})


@bp.route("/api/img/<img_type>/count")
def image_count(img_type):
    if img_type not in utils.get_image_types():
        abort(404, description=f"Invalid image type '{img_type}'")

    info = utils.get_images_info(img_type)
    return jsonify(
        {
            "type": img_type,
            "horizontal_count": len(info["horizontal"]),
            "vertical_count": len(info["vertical"]),
            "total_count": len(info["horizontal"]) + len(info["vertical"]),
        }
    )



"""
直接返回随机图片 (二进制流)
`/random_image/<type>`
"""
@bp.route("/random_image/<img_type>", methods=["GET"])
def random_image_direct(img_type):
    # 获取orientation参数
    orientation = request.args.get("orientation", None)

    # 如果未指定orientation，根据设备UA判断
    if not orientation:
        user_agent = request.user_agent.string.lower()
        # 检测移动设备关键词
        mobile_keywords = ["iphone", "ipad", "symbian", "mobile", "android"]
        if any(keyword in user_agent for keyword in mobile_keywords):
            orientation = "vertical"  # 移动设备默认返回竖屏
        elif "macos" in user_agent or "windows" in user_agent:
            orientation = "horizontal"  # 桌面设备默认返回横屏
        # 无UA或未匹配到则保持为None，让utils处理随机选择

    result = utils.get_random_image_path(img_type, orientation)
    if not result:
        abort(404, description=f"No images found for type '{img_type}'")

    image_path, _ = result
    return send_file(image_path)


"""
返回图片信息的JSON
`/random_image/j/<type>`
"""
@bp.route("/random_image/j/<img_type>", methods=["GET"])
def random_image_json(img_type):
    # 获取orientation参数
    orientation = request.args.get("orientation", None)

    # 如果未指定orientation，根据设备UA判断
    if not orientation:
        user_agent = request.user_agent.string.lower()
        # 检测移动设备关键词
        mobile_keywords = ["iphone", "ipad", "symbian", "mobile", "android"]
        if any(keyword in user_agent for keyword in mobile_keywords):
            orientation = "vertical"  # 移动设备默认返回竖屏
        elif "macos" in user_agent or "windows" in user_agent:
            orientation = "horizontal"  # 桌面设备默认返回横屏
        # 无UA或未匹配到则保持为None，让utils处理随机选择

    result = utils.get_random_image_path(img_type, orientation)
    if not result:
        abort(404, description=f"No images found for type '{img_type}'")

    image_path, actual_orientation = result
    filename = os.path.basename(image_path)

    try:
        size = os.path.getsize(image_path)
    except OSError:
        size = 0

    # 获取当前请求的基地址
    base_url = request.host_url.rstrip("/")

    return jsonify(
        {
            "type": img_type,
            "orientation": actual_orientation,
            "filename": filename,
            "path": f"{base_url}/image/{img_type}/{actual_orientation}/{filename}",
            "size": size,
            "direct_url": f"{base_url}/random_image/{img_type}?orientation={actual_orientation}",
            "redirect_url": f"{base_url}/random_image/g/{img_type}?orientation={actual_orientation}",
            "requested_orientation": orientation,  # 返回客户端请求的方向
        }
    )


"""
重定向到图片URL
`/random_image/g/<type>`
"""
@bp.route("/random_image/g/<img_type>", methods=["GET"])
def random_image_redirect(img_type):
    # 获取orientation参数
    orientation = request.args.get("orientation", None)

    # 如果未指定orientation，根据设备UA判断
    if not orientation:
        user_agent = request.user_agent.string.lower()
        # 检测移动设备关键词
        mobile_keywords = ["iphone", "ipad", "symbian", "mobile", "android"]
        if any(keyword in user_agent for keyword in mobile_keywords):
            orientation = "vertical"  # 移动设备默认返回竖屏
        elif "macos" in user_agent or "windows" in user_agent:
            orientation = "horizontal"  # 桌面设备默认返回横屏
        # 无UA或未匹配到则保持为None，让utils处理随机选择

    result = utils.get_random_image_path(img_type, orientation)
    if not result:
        abort(404, description=f"No images found for type '{img_type}'")

    image_path, actual_orientation = result
    filename = os.path.basename(image_path)
    return redirect(f"/image/{img_type}/{actual_orientation}/{filename}")


@bp.route("/image/<img_type>/<orientation>/<filename>")
def serve_image(img_type, orientation, filename):
    # 安全验证
    if img_type not in utils.get_image_types():
        abort(404, description=f"Invalid image type '{img_type}'")

    if orientation not in ["horizontal", "vertical"]:
        abort(400, description=f"Invalid orientation '{orientation}'")

    # 构建路径
    image_base = current_app.config["IMAGE_BASE"]
    image_path = os.path.join(image_base, img_type, orientation, filename)

    # 验证文件存在
    if not os.path.isfile(image_path):
        abort(404, description="Image not found")

    # 验证文件扩展名
    ext = filename.split(".")[-1].lower()
    if ext not in current_app.config["ALLOWED_EXTENSIONS"]:
        abort(400, description="Invalid file type")

    return send_file(image_path)
