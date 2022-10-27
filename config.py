# ===========
# 脱敏的生产环境配置（严禁记录密钥）
# 开发测试配置可放在 configs 文件夹下（已 gitignore）或项目外
# 至少要修改标注为 必填 的几个项目
# ===========
from os import environ as env

# -----------
# 基础设置
# -----------
APP_NAME = "moetran"
APP_VERSION = "0.5.1020"
APP_SITE_NAME = env.get("APP_SITE_NAME", "漫画译注器协作版")
APP_SITE_URL = env.get("APP_SITE_URL")
SECRET_KEY = env["SECRET_KEY"] # 必填 - 密钥
# 密钥：没有明确格式，只用来对密码加密（修改密钥后，所有之前的用户就无法登录了，需要重置密码）
DEBUG = False
TESTING = False
MAX_CONTENT_LENGTH = 20 * 1024 * 1024
# -----------
# Mongo 数据库
# -----------
DB_URI = (
    f"{env['MONGODB_URL']}/{APP_NAME}?authSource=admin"
) # 必填 - MangoDB连接串
# 测试环境请把下面一行前面的 # 删除然后修改下面一行的内容：
# DB_URI = (f"mongodb://user:password@127.0.0.1:27017/{APP_NAME}?authSource=admin")
# 如果MangoDB没有设置账号和密码，可以删除 user:password@ 这段，具体请搜索MangoDB连接串
# -----------
# i18n
# -----------
BABEL_DEFAULT_LOCALE = "zh_Hans_CN"
BABEL_DEFAULT_TIMEZONE = "UTC"
# -----------
# 其他设置
# -----------
CONFIRM_EMAIL_WAIT_SECONDS = 60  # 重新发送确认邮箱邮件发送等待时间
RESET_EMAIL_WAIT_SECONDS = 60  # 重置邮箱验证码邮件发送等待时间
RESET_PASSWORD_WAIT_SECONDS = 60  # 重置密码邮件发送等待时间
PLAN_FINISH_DELTA = 7 * 24 * 60 * 60  # 计划完结延时时间
PLAN_DELETE_DELTA = 7 * 24 * 60 * 60  # 计划删除延时时间
# -----------
# 默认设置
# -----------
DEFAULT_USER_AVATAR = None
DEFAULT_TEAM_AVATAR = None
# -----------
# 文件上传相关设置
# local = 本地文件
# oss = 阿里云OSS
# -----------
FILE_CACHE_TYPE = env.get("FILE_CACHE_TYPE", "local")
# -----------
# 本地文件存储相关
# -----------
if FILE_CACHE_TYPE == "local":
    FILE_PREFIX = "files"
    USER_AVATAR_PREFIX = "avatars/user"
    TEAM_AVATAR_PREFIX = "avatars/team"
    OUTPUT_PREFIX = "output"
    PROJECT_PREDIX = "project"
    FILE_SCHEME = env.get('FILE_SCHEME', 'http')
    # 如果需要独立文件的访问地址，请配置包括协议的完整地址。此时上方的协议变量会失效
    # 例如：https://files.moetran.com/
    FILE_DOMAIN = env.get('FILE_DOMAIN')
    
# -----------
# OSS 暂时移除了相关配置
# -----------
# if FILE_CACHE_TYPE == "oss":

# -----------
# EMAIL SMTP
# -----------
EMAIL_SMTP_HOST = env.get("EMAIL_SMTP_HOST", "smtp.163.com") # 必填 - SMTP服务器地址
EMAIL_SMTP_PORT = env.get("EMAIL_SMTP_PORT", 465) # 必填 - SMTP服务器端口
EMAIL_USE_SSL = True
EMAIL_ADDRESS = env.get("EMAIL_ADDRESS", "no-reply@moetran.com")
EMAIL_USERNAME = env.get("EMAIL_USERNAME", "")
EMAIL_PASSWORD = env.get("EMAIL_PASSWORD", "")
EMAIL_REPLY_ADDRESS = env.get("EMAIL_ADDRESS", "admin@moetran.com")
EMAIL_ERROR_ADDRESS = env.get("EMAIL_ADDRESS", "admin@moetran.com")
# -----------
# Celery
# -----------
CELERY_BROKER_URL = (
    f"{env['RABBITMQ_URL']}/{APP_NAME}"
)
CELERY_BACKEND_URL = DB_URI
CELERY_MONGODB_BACKEND_SETTINGS = {
    "database": APP_NAME,
    "taskmeta_collection": "celery_taskmeta",
}
# -----------
# APIKit
# -----------
APIKIT_PAGINATION_PAGE_KEY = "page"
APIKIT_PAGINATION_LIMIT_KEY = "limit"
APIKIT_PAGINATION_DEFAULT_LIMIT = 30
APIKIT_PAGINATION_MAX_LIMIT = 100
APIKIT_ACCESS_CONTROL_ALLOW_HEADERS = [
    "Authorization",
    "Content-Type",
    "X-Requested-With",
]

# -----------
# 配置可访问域名
# -----------
allow_origin = env.get("ALLOW_ORIGIN", "*")
if allow_origin == "*":
    APIKIT_ACCESS_CONTROL_ALLOW_ORIGIN = allow_origin
elif allow_origin.count(',') > 0:
    allow_origins = allow_origin.split(',')
    APIKIT_ACCESS_CONTROL_ALLOW_ORIGIN = allow_origins
