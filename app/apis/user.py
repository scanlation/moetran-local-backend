"""
关于用户的API
"""
from flask_babel import gettext

from app.core.responses import MoePagination
from app.core.views import MoeAPIView
from app.decorators.auth import admin_required, token_required
from app.decorators.url import fetch_model
from app.exceptions import RequestDataEmptyError, UserNotExistError
from app.exceptions.auth import EmailNotInWhitelistError
from app.models.site_setting import SiteSetting
from app.models.user import User
from app.validators import RegisterSchema
from app.validators.admin import AdminStatusSchema
from app.validators.auth import AdminEditUserPasswordSchema, AdminRegisterSchema


class UserListAPI(MoeAPIView):
    @token_required
    def get(self):
        """
        @api {get} /v1/users?word=<word> 获取用户列表
        @apiVersion 1.0.0
        @apiName get_users
        @apiGroup Users
        @apiUse APIHeader
        @apiUse TokenHeader

        @apiParam {String} word 搜索词

        @apiSuccessExample {json} 返回示例
        [
            {
                "avatar": null,
                "id": "5911930d7e4b036e2df3a910",
                "name": "123123",
                "signature": "這個用戶還沒有簽名"
            }
        ]

        @apiUse NeedTokenError
        @apiUse BadTokenError
        """
        query = self.get_query()
        # word 不可为空
        if "word" not in query or query["word"] == "":
            raise RequestDataEmptyError
        p = MoePagination()
        objects = (
            User.objects(name__icontains=query["word"]).skip(p.skip).limit(p.limit)
        )
        return p.set_objects(objects)


class UserAPI(MoeAPIView):
    def get(self, name):
        """
        @api {get} /v1/users/<name> 获取用户公开资料
        @apiVersion 1.0.0
        @apiName get_user_public_info
        @apiGroup Users
        @apiUse APIHeader

        @apiParam {String} name 用户名

        @apiSuccessExample {json} 返回示例
        {
          "avatar": null,
          "name": "123123",
          "signature": "这个用户还没有签名"
        }

        @apiUse UserNotExistError
        """
        user = User.by_name(name)
        if user:
            return user.to_api()
        else:
            raise UserNotExistError

    def post(self):
        """
        @api {post} /v1/users 新建用户
        @apiVersion 1.0.0
        @apiName add_user
        @apiGroup Users
        @apiUse APIHeader

        @apiParam {String}      email        邮箱
        @apiParam {String}      name         昵称
        @apiParam {String}      password     密码
        @apiParam {String}      vCode        邮箱验证码内容
        @apiParamExample {json} 请求示例
        {
            "email":"123@123.com",
            "name":"123123",
            "password":"123123",
            "v_code":"Qbip9W"
        }

        @apiSuccess {String} msg 提示消息
        @apiSuccessExample {json} 返回示例
        {
            "message": "注册成功",
            "token": "xxxxxxxxx"
        }

        @apiUse ValidateError
        """
        data = self.get_json(RegisterSchema())
        # 检查白名单
        site_setting = SiteSetting.get()
        if site_setting.enable_whitelist:
            if data["email"] not in site_setting.whitelist_emails:
                raise EmailNotInWhitelistError
        # 创建用户
        user = User.create(
            email=data["email"], name=data["name"], password=data["password"]
        )
        # 生成token
        token = user.generate_token()
        return {"message": gettext("注册成功"), "token": token}


class AdminUserListAPI(MoeAPIView):
    @admin_required
    def get(self):
        """
        @api {get} /v1/admin/users 管理后台获取用户列表
        @apiVersion 1.0.0
        @apiName get_admin_users
        @apiGroup Admin
        @apiUse APIHeader
        @apiUse TokenHeader

        @apiSuccessExample {json} 返回示例
        [
            {
                "avatar": null,
                "id": "5911930d7e4b036e2df3a910",
                "name": "123123",
                "signature": "這個用戶還沒有簽名"
            }
        ]

        @apiUse NeedTokenError
        @apiUse BadTokenError
        """
        query = self.get_query()
        # word 不可为空
        p = MoePagination()
        word = query["word"]
        objects = (
            (
                User.objects(name__icontains=query["word"])
                .skip(p.skip)
                .limit(p.limit)
                .order_by("-create_time")
            )
            if word
            else User.objects.skip(p.skip).limit(p.limit).order_by("-create_time")
        )
        return p.set_objects(objects)

    @admin_required
    def post(self):
        """
        @api {post} /v1/admin/users 管理后台新建用户
        """
        data = self.get_json(AdminRegisterSchema())
        # 创建用户
        User.create(email=data["email"], name=data["name"], password=data["password"])
        return {"message": gettext("注册成功")}


class AdminUserAPI(MoeAPIView):
    @admin_required
    @fetch_model(User)
    def put(self, user):
        """
        @api {put} /v1/admin/users/<user_id> 重置用户密码
        """
        data = self.get_json(AdminEditUserPasswordSchema())
        user.password = data["password"]
        user.save()
        return {"message": gettext("修改成功")}


class AdminUserAdminStatusAPI(MoeAPIView):
    @admin_required
    def put(self):
        """
        @api {put} /v1/admin/admin-status 修改用户的管理员状态
        @apiVersion 1.0.0
        @apiName put_admin_status
        @apiGroup Admin
        @apiUse APIHeader
        @apiUse TokenHeader

        @apiParam {String} user_id 用户Id
        @apiParam {Boolean} is_admin 是否是管理员

        @apiSuccessExample {json} 返回示例
        {
            "data": "修改成功"
        }

        @apiUse NeedTokenError
        @apiUse BadTokenError
        """
        data = self.get_json(AdminStatusSchema())
        user = User.by_id(data["user_id"])
        if user is None:
            raise UserNotExistError
        user.admin = data["status"]
        user.save()
        return {
            "message": gettext("修改成功"),
        }
