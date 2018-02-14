from flask import Blueprint
from flask_restful import Api
from .user_api import ListUser, SingleUser


auth = Blueprint(name="auth", import_name=__name__, url_prefix="/api/auth", static_folder="static",
                 template_folder="templates")
authApi = Api(auth)

authApi.add_resource(ListUser, "/users")
authApi.add_resource(SingleUser, "/user/<int:user_id>")

from . import views
