import os

from celery import Celery
from celery.signals import worker_shutting_down
from celery.utils.log import get_task_logger
from flask import Flask, g, request, render_template, url_for
from flask_apikit import APIKit
from flask_babel import Babel

from app.constants.locale import Locale
# from app.services.google_storage import GoogleStorage
# from app.services.oss import OSS
from app.services.local_file import LocalFile
from app.utils.logging import configure_logger, logger

from .apis import register_apis

# 基本路径
APP_PATH = os.path.abspath(os.path.dirname(__file__))
FILE_PATH = os.path.abspath(os.path.join(APP_PATH, "..", "files"))  # 一般文件
TMP_PATH = os.path.abspath(os.path.join(FILE_PATH, "tmp"))  # 临时文件存放地址
STATIC_PATH = None # 文件存储目录仅在本地存储方式时，由环境变量赋值

# 插件
babel = Babel()
# oss = None
localFile = LocalFile()
fileStorage = localFile
# gs_vision = GoogleStorage()
apikit = APIKit()

config_path_env = "CONFIG_PATH"
"""
这里要先配置环境变量
测试环境：
CONFIG_PATH=../configs/dev.py
对应 README 第4步中自己创建的配置
docker正式环境：
CONFIG_PATH=../config.py
其他必填的参数全部写在docker的环境变量里面
"""


def create_app():
    app = Flask(__name__)
    app.config.from_envvar(config_path_env)  # 获取配置文件
    configure_logger(app)  # 配置日志记录(放在最前,会被下面调用)

    logger.info("-" * 50)
    logger.info("使用配置文件: {}".format(os.environ.get(config_path_env)))
    # 连接数据库
    from app.models import connect_db

    connect_db(app.config)
    # 注册api蓝本
    register_apis(app)
    # 初始化角色，语言
    from app.models.language import Language
    from app.models.project import ProjectRole
    from app.models.team import TeamRole

    TeamRole.init_system_roles()
    ProjectRole.init_system_roles()
    Language.init_system_languages()
    # 初始化插件
    babel.init_app(app)
    apikit.init_app(app)
    # 在返回的头部信息中添加"Api-Version"头
    @app.after_request
    def after_request(resp):
        resp.headers["X-Api-Version"] = '{} Version:{}'.format(app.config['APP_NAME'], app.config['APP_VERSION'])
        return resp
    @app.errorhandler(404)
    def page_not_found(error):
        site_url = app.config.get("APP_SITE_URL")
        # if (site_url is None):
        #   site_url = url_for('.index', _external=True)
        tpl_data = {
            'site_name': app.config.get("APP_SITE_NAME"),
            'site_url': site_url
        }
        return render_template("index.html", **tpl_data)

    logger.info("-" * 50)
    logger.info('{} Version.{}'.format(app.config['APP_NAME'], app.config['APP_VERSION']))
    logger.info("站点支持语言: " + str([str(i) for i in babel.list_translations()]))
    # 文件储存
    logger.info("-" * 50)
    logger.info("文件存储方式：" + app.config["FILE_CACHE_TYPE"])
    """
    if app.config["FILE_CACHE_TYPE"] == "oss":
        oss = OSS()
        oss.init(app.config)
        fileStorage = oss
    """
    if app.config["FILE_CACHE_TYPE"] == "local":
        # setattr(localFile, 'STATIC_PATH', STATIC_PATH)
        localFile.init(app.config)
        STATIC_PATH = localFile.STATIC_PATH
        logger.info("文件存储目录：" + STATIC_PATH)
        fileStorage = localFile

    # 检测 env_files 是否挂载成功
    """
    logger.info("-" * 50)
    json_exists = os.path.exists(
        app.config["GOOGLE_STORAGE_MOEFLOW_VISION_TMP"]["JSON"]
    )
    logger.info(f"挂载 env_files：{json_exists}")
    """
    # from app.tasks.ocr import recover_ocr_tasks

    # recover_ocr_tasks()
    return app


CELERY_ABOUT_TO_SHUTDOWN_FLAG = "CELERY_ABOUT_TO_SHUTDOWN_FLAG"


def delete_about_to_shutdown_flag():
    try:
        os.rmdir(CELERY_ABOUT_TO_SHUTDOWN_FLAG)
    except Exception:
        pass


def create_celery():
    delete_about_to_shutdown_flag()
    # 为celery创建app
    app = Flask(__name__)
    app.config.from_envvar(config_path_env)  # 获取配置文件,仅从环境变量读取,均需要配置环境变量
    # 通过app配置创建celery实例
    celery = Celery(
        app.name,
        broker=app.config["CELERY_BROKER_URL"],
        backend=app.config["CELERY_BACKEND_URL"],
        mongodb_backend_settings=app.config["CELERY_MONGODB_BACKEND_SETTINGS"],
    )
    celery.conf.update({"app_config": app.config})
    celery.autodiscover_tasks(
        packages=[
            "app.tasks.email",
            "app.tasks.file_parse",
            "app.tasks.output_project",
            # "app.tasks.ocr",
            "app.tasks.import_from_labelplus",
            "app.tasks.thumbnail"
        ],
        related_name=None,
    )
    celery_logger = get_task_logger(app.name)
    celery_logger.info("-" * 50)
    celery_logger.info('{} Version.{}'.format(app.config['APP_NAME'], app.config['APP_VERSION']))
    celery_logger.info("-" * 50)
    celery.conf.task_routes = {
        # "tasks.ocr_task": {"queue": "ocr"},
        "tasks.thumbnail_task": {"queue": "output"},
        "tasks.output_project_task": {"queue": "output"},
        "tasks.import_from_labelplus_task": {"queue": "output"},
    }
    return celery


celery = create_celery()


def create_about_to_shutdown_flag():
    try:
        os.mkdir(CELERY_ABOUT_TO_SHUTDOWN_FLAG)
    except Exception:
        pass


@worker_shutting_down.connect
def when_shutdown(**kwargs):
    create_about_to_shutdown_flag()


def about_to_shutdown():
    """检测 Celery 是否将要关闭"""
    return os.path.isdir(CELERY_ABOUT_TO_SHUTDOWN_FLAG)


@babel.localeselector
def get_locale():
    current_user = g.get("current_user")
    if (
        current_user
        and current_user.locale
        and current_user.locale != "auto"
        and current_user.locale in Locale.ids()
    ):
        return current_user.locale
    return request.accept_languages.best_match(["zh_CN", "zh_TW", "zh", "en_US", "en"])


# @babel.timezoneselector
# def get_timezone():
#     # TODO 弄清 timezone 是什么东西
#     current_user = g.get('current_user')
#     if current_user:
#         if current_user.timezone:
#             return current_user.timezone
