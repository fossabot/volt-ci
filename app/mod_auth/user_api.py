from flask_restful import Resource, abort
from flask_login import login_required, current_user
from .models import UserAccount, UserProfile


class SingleUser(Resource):

    method_decorators = [login_required]

    def get(self, user_id: str) -> tuple:
        """
        Handles GET requests to fetch a single user with the user_id provided
        :param user_id: User id
        :type user_id str
        :return: Data dictionary and the response code
        :rtype: tuple
        """

        if current_user.id != user_id:
            abort(403, message="You have insufficient permissions to access this resource")

        user = UserAccount.query.filter_by(id=user_id).one()

        if user:
            user_profile = UserProfile.query.filter_by(current_user.user_profile_id)
            data = dict(
                id=user.id,
                first_name=user_profile.first_name,
                last_name=user_profile.last_name,
                member_since=user.member_since,
                username=current_user.user_name,
                email=user.email,
                created_on=user.date_created,
                last_seen=user.last_seen
            )

            return data, 200

        else:
            abort(404, message="No such user exists")


class ListUser(Resource):
    pass
