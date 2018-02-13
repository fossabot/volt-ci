from flask_restful import Resource


class PhotoListResource(Resource):

    def get(self):
        """
        Handle GET requests
        :return: JSON response as a dict
        :rtype: dict
        """
        pass


class PhotoSingleResource(Resource):
    def get(self, photo_id):
        """
        Handle GET requests
        :param photo_id: Id of photo to get
        :return: JSON response as a dict
        :rtype: dict
        """
        pass

    def delete(self, photo_id):
        """
        Handle DELETE requests
        :param photo_id: Photo id
        :return: JSON response as a dictionary
        """
        pass

    def post(self):
        """
        POST request
        :return:
        """
        pass
