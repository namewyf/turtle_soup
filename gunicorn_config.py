"""
Gunicorn 配置文件
用于本地和生产环境的统一配置
"""

import multiprocessing
import os

# 服务器绑定
bind = f"0.0.0.0:{os.environ.get('PORT', 5002)}"

# Worker 进程数
workers = os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1)

# Worker 类型
worker_class = 'sync'

# 超时时间
timeout = 120

# 重载（仅开发环境）
reload = os.environ.get('GUNICORN_RELOAD', 'false').lower() == 'true'

# 日志级别
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')

# 访问日志格式
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 错误日志
errorlog = '-'

# 预加载应用（确保初始化代码执行）
preload_app = True

# 进程名称
proc_name = 'turtle_soup'

# 在 Worker 启动前执行
def when_ready(server):
    server.log.info("Gunicorn 服务器已准备就绪")

def worker_int(worker):
    worker.log.info("Worker 收到 INT 或 QUIT 信号")

def pre_fork(server, worker):
    server.log.info(f"Worker 即将创建: {worker}")

def post_fork(server, worker):
    server.log.info(f"Worker 已创建: {worker.pid}")

def pre_exec(server):
    server.log.info("新的主进程即将 fork")

def on_starting(server):
    server.log.info("Gunicorn 正在启动")