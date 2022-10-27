# 漫画译注器协作版[MoeTran]后端(本地存储版)项目

基于萌翻开源代码修改的本地存储版本，目前为Alpha预览版本。萌翻[MoeFlow]原版前端目前已经采用了这边提交的 `Pull Request` ，使用萌翻原版的最新版本可以正常调用本后端的功能。

关于此项目的技术支持和问题反馈，请加群：`451050931` 萌翻的反馈群里面目前也能得到这个项目的技术支持（询问时注明是漫画译注器协作版项目），但后续会进行拆分。

## 安装步骤

1. 安装 Python 3.8.13 版本以上，3.10 版本以下，推荐 `3.9.2`
2. 依赖环境MangoDB、Erlang、RabbitMQ
3. `pip install -r requirements.txt` （这一步如果Windows有报错，请在环境变量里面加 `PYTHONUTF8=1` ）
4. 以 `/config.py` 为模板创建 `/configs/dev.py` 用于开发（此目录已被 git ignore）
5. 开发时，请直接在 `/configs/dev.py` 文件里面修改必填的配置
6. 注意配置环境变量 `CONFIG_PATH=../configs/dev.py` 不然运行时会报错。
7. 运行主进程： `python manage.py run`
8. 在 `DEBUG` 开启的情况下，注册等验证码信息，直接看命令行输出的日志信息。
9. 导入、导出等功能需要依赖两个celery worker进程，调试时可按另附的步骤启动。

## 配置Celery

1. 如果使用Windows跑Celery Worker，需要先安装 `eventlet` 并修改参数，否则会提示： `not enough values to unpack (expected 3, got 0)`
2. *(可选)* Windows安装 `eventlet` 请执行： `pip install eventlet`
3. 两个worker需要启动两个命令行（**这里的方案使用 Windows 的 Powershell 举例**），并配置环境变量：`$env.CONFIG_PATH=../configs/dev.py` 。（环境变量仅在当前窗口中生效，其他平台请自行搜索设置环境变量的方法）
4. 启动主要 Celery Worker (发送邮件、分析术语)，请执行：`celery -A app.celery worker -n default -P eventlet --loglevel=info`
5. 启动输出用 Celery Worker (导入项目、生成缩略图、导出翻译、导出项目)，请执行：`celery -A app.celery worker -Q output -n output -P eventlet --loglevel=info`
6. 非Windows环境如果有报错，请去掉命令中的 `-P eventlet` 一段。

## 版本修改内容一览

### Version.0.5.1010

1. 修改部分没做本地化的位置（例如：首页、邮件），方便修改网站名称、标题、域名等信息。
2. 调整config.py中的配置格式，部分配置有默认值可选。
3. 将原先上传阿里云OSS的配置移除，**目前仅支持本地存储！**
4. 本地存储的目录为根目录下的 `storage` 文件夹，可修改但目前未测试。
5. 在上传后新增生成缩略图的 Celery 任务
6. 调整输出的翻译文本格式为 `utf-8`
7. 导出的文件添加强制下载的HTTP头，翻译稿也能直接弹出下载窗口了。
8. 调整输出完整打包时的方案，不再包含Photoshop脚本等不方便维护的信息。
9. 调整创建项目、创建团队时的部分参数，减少前端需配置的默认值。
10. 移除ORC自动标注、敏感词检测、图片审核等依赖API的功能点，减少配置。

### Version.0.5.1020

1. 修改后端首页模版、增加 404 跳转到首页的代码。方便将前后端项目进行合并。（相关操作说明请参考前端帮助文件中对应段落！）
2. 支持链接输出时强制加 `https` 协议，解决Chrome下载文件时提示文件不安全的问题。
3. 修正完整打包导出时，图片复制参数出错造成没有图片的问题。

## 关于测试

由于项目开发比较仓促，暂时没有做自动化测试。原有的自动化项目可能都是关于OSS文件存储相关的，对目前的项目没有太大意义。

如果你在测试中发现什么问题，优先到反馈群里面通知修改。版本未稳定前不支持用Issues反馈错误。
