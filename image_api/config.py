import os

# 基础配置
STWQMC_NAME = 'Random Image API Service'
STWQMC_VERSION = '0.3'

# 支持的图片类型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# 限制每分钟最多XXX次请求
LIMITER_BAPC = 120

# 文件路径获取
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
THEME_DIR = os.path.join(PROJECT_ROOT, './theme')
IMAGE_BASE = os.path.join(BASE_DIR, '../upur')
