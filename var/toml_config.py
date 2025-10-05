# -*- coding: utf-8 -*-
import tomllib
import os



# 获取配置文件路径
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.toml')

# 读取TOML配置
with open(config_path, 'rb') as f:
    config = tomllib.load(f)

# 导出配置项
# 使用相对于项目根目录的路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_BASE = os.path.join(PROJECT_ROOT, config['paths']['image_base'])
TEXT_BASE = os.path.join(PROJECT_ROOT, config['paths']['text_base'])
ALLOWED_EXTENSIONS = set(config['extensions']['allowed'])
THEME_DIR = os.path.join(PROJECT_ROOT, config['paths']['theme_dir'])
LIMITER_BAPC = config['limiter']['requests_per_minute']
STWQMC_NAME = config['app']['name']
STWQMC_VERSION = config['app']['version']
