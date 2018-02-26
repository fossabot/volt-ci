"""
Test user api resource
"""
from app.mod_auth.models import UserAccount, UserProfile
from flask import json
import base64


def test_get_single_user_authenticated(db, session, client):
    """Test to get a user"""
    pass
    