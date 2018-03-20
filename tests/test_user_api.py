"""
Test user api resource
"""
from app.mod_auth.models import UserAccount, UserProfile
from flask import json
import base64


def test_get_single_user_authenticated(db, session, client):
    """Test to get a user"""
    data = {'username': 'authed', 'email': 'authed@example.com', 'password': 'foobar'}
    user = UserAccount(**data)
    session.add(user)
    session.commit()
    
    creds = base64.b64encode(b'{0}:{1}'.format(user.username, data['password'])).decode('utf-8')
    
    response = client.get('/users/{}'.format(user.id),
    headers={'Authorization': 'Basic ' + creds})
    assert response.status_code == 200
    assert json.loads(response.get_data())['id'] == user.id
