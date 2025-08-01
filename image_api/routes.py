from flask import Blueprint, jsonify, send_file, redirect, abort, current_app, request
from . import utils
from .config import STWQMC_NAME, STWQMC_VERSION
import os


bp = Blueprint('routes', __name__)

@bp.route('/api')
def api_status():
    return jsonify({
        'status': '200',
        'message': STWQMC_NAME,
        'version': STWQMC_VERSION
    })

@bp.route('/api/img/types')
def get_image_types_api():
    return jsonify({
        'types': utils.get_image_types(),
        'count': len(utils.get_image_types())
    })

@bp.route('/random_image/<img_type>')
def random_image_direct(img_type):
    # 获取orientation参数
    orientation = request.args.get('orientation', None)
    
    result = utils.get_random_image_path(img_type, orientation)
    if not result:
        abort(404, description=f"No images found for type '{img_type}'")
    
    image_path, _ = result
    return send_file(image_path)

@bp.route('/random_image/j/<img_type>')
def random_image_json(img_type):
    # 获取orientation参数
    orientation = request.args.get('orientation', None)
    
    result = utils.get_random_image_path(img_type, orientation)
    if not result:
        abort(404, description=f"No images found for type '{img_type}'")
    
    image_path, actual_orientation = result
    filename = os.path.basename(image_path)
    
    try:
        size = os.path.getsize(image_path)
    except:
        size = 0
    
    # 获取当前请求的基地址
    base_url = request.host_url.rstrip('/')
    
    return jsonify({
        'type': img_type,
        'orientation': actual_orientation,
        'filename': filename,
        'path': f"{base_url}/image/{img_type}/{actual_orientation}/{filename}",
        'size': size,
        'direct_url': f"{base_url}/random_image/{img_type}?orientation={actual_orientation}",
        'redirect_url': f"{base_url}/random_image/g/{img_type}?orientation={actual_orientation}",
        'requested_orientation': orientation  # 返回客户端请求的方向
    })

@bp.route('/random_image/g/<img_type>')
def random_image_redirect(img_type):
    # 获取orientation参数
    orientation = request.args.get('orientation', None)
    
    result = utils.get_random_image_path(img_type, orientation)
    if not result:
        abort(404, description=f"No images found for type '{img_type}'")
    
    image_path, actual_orientation = result
    filename = os.path.basename(image_path)
    return redirect(f"/image/{img_type}/{actual_orientation}/{filename}")

@bp.route('/image/<img_type>/<orientation>/<filename>')
def serve_image(img_type, orientation, filename):
    # 安全验证
    if img_type not in utils.get_image_types():
        abort(404, description=f"Invalid image type '{img_type}'")
    
    if orientation not in ['horizontal', 'vertical']:
        abort(400, description=f"Invalid orientation '{orientation}'")
    
    # 构建路径
    image_base = current_app.config['IMAGE_BASE']
    image_path = os.path.join(image_base, img_type, orientation, filename)
    
    # 验证文件存在
    if not os.path.isfile(image_path):
        abort(404, description="Image not found")
    
    # 验证文件扩展名
    ext = filename.split('.')[-1].lower()
    if ext not in current_app.config['ALLOWED_EXTENSIONS']:
        abort(400, description="Invalid file type")
    
    return send_file(image_path)

@bp.route('/api/img/<img_type>/count')
def image_count(img_type):
    if img_type not in utils.get_image_types():
        abort(404, description=f"Invalid image type '{img_type}'")
    
    info = utils.get_images_info(img_type)
    return jsonify({
        'type': img_type,
        'horizontal_count': len(info['horizontal']),
        'vertical_count': len(info['vertical']),
        'total_count': len(info['horizontal']) + len(info['vertical'])
    })

@bp.route('/api/img/<img_type>/list')
def image_list(img_type):
    if img_type not in utils.get_image_types():
        abort(404, description=f"Invalid image type '{img_type}'")
    
    base_url = request.host_url.rstrip('/')
    
    info = utils.get_images_info(img_type, base_url)
    return jsonify({
        'type': img_type,
        'images': info
    })