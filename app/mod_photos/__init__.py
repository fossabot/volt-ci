from flask import Blueprint
from flask_restful import Api
from .resources.photo_resource import PhotoListResource, PhotoSingleResource

photos = Blueprint(name="photos", import_name=__name__, url_prefix="/api/photos", static_folder="static",
                   template_folder="templates")
api = Api(photos)

routes = [
    "/",
    "/<int:photo_id>"
]

api.add_resource(PhotoSingleResource, routes[0])
api.add_resource(PhotoListResource, routes[1])


from . import views

