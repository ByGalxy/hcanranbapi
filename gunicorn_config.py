"""
-*- coding: utf-8 -*-
Gunicorn配置文件
"""
import multiprocessing

# 绑定的主机和端口
bind = "0.0.0.0:5000"

# 工作进程数量，通常设置为CPU核心数*2+1
workers = multiprocessing.cpu_count() * 2 + 1

# 每个工作进程的线程数
threads = 2

# 工作方式，使用gevent异步方式
worker_class = "sync"

# 最大并发数
worker_connections = 1000

# 请求超时时间（秒）
timeout = 30

# 保持活动连接的时间（秒）
keepalive = 2

# 访问日志格式
accesslog = "-"  # 输出到标准输出
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# 错误日志格式
errorlog = "-"  # 输出到标准错误
loglevel = "info"

# 进程ID文件
pidfile = "gunicorn.pid"

# 守护进程模式（后台运行）
daemon = False

# 环境变量
env = {"PRODUCTION": "True"}

# 当代码有修改时自动重启（开发环境可用）
reload = False

# 最大请求数，超过后自动重启工作进程
exit_on_timeout = True

# 服务器标识
syslog = False

# 进程名称
proc_name = "hcanranbapi"

# 预加载应用，减少内存使用和启动时间
preload_app = True