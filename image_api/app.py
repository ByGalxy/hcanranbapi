from flask import Flask, send_from_directory, make_response, render_template_string, request
from flask_cors import CORS
from .config import IMAGE_BASE, ALLOWED_EXTENSIONS, THEME_DIR, LIMITER_BAPC
from .routes import bp
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # 配置设置
    app.config.update({
        'IMAGE_BASE': IMAGE_BASE,
        'ALLOWED_EXTENSIONS': ALLOWED_EXTENSIONS,
        'THEME_DIR': THEME_DIR
    })
    
    app.register_blueprint(bp)
    
    # 自定义错误处理器
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return render_error_page('429.html'), 429
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_error_page('404.html'), 404

    def render_error_page(page_name):
        """
        渲染错误页面
        """
        misstatement_dir = os.path.join(app.config['THEME_DIR'], 'misstatement')
        page_path = os.path.join(misstatement_dir, page_name)
        
        if not os.path.isfile(page_path):
            return f"<h1>Error</h1><p>{page_name.replace('.html', '')} occurred</p>"
        
        with open(page_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 替换相对路径为绝对路径
        base_url = request.host_url.rstrip('/')
        content = content.replace('href="/', f'href="{base_url}/')
        content = content.replace('src="/', f'src="{base_url}/')
        
        return content
    
    # 服务前端静态文件（包括错误页面）
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        theme_dir = app.config['THEME_DIR']
        misstatement_dir = os.path.join(theme_dir, 'misstatement')
        
        # 特殊处理错误页面
        if path in ['429.html', '404.html', '500.html']:
            return send_from_directory(misstatement_dir, path)
        
        # 检查请求的路径是否存在
        full_path = os.path.join(theme_dir, path)
        
        if path == "" or not os.path.exists(full_path) or os.path.isdir(full_path):
            # 返回 index.html 用于前端路由
            # 如果有这样的需求可以改
            return send_from_directory(theme_dir, '404.html')
        
        # 其他静态文件
        return send_from_directory(theme_dir, path)

    def redis_limiter_memory():
        # 初始化限流器，使用内存存储
        limiter = Limiter(
            key_func=get_remote_address,
            app=app,
            default_limits=[f"{LIMITER_BAPC}/minute"],
            storage_uri="memory://"
        )

    redis_limiter_memory()
    
    return app