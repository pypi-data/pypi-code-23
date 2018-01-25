import re

from cms_qe_auth.models import User
from pytest_data import use_data


@use_data(user_data={'username': 'testuser', 'password': 'testpass'})
def test_login(client, user):
    res = client.post('/en/auth/login/', {'username': 'testuser', 'password': 'testpass'})
    assert res.status_code == 302


def test_register(mailoutbox, client):
    assert len(mailoutbox) == 0
    assert not User.objects.filter(username='testuser')

    user = _register_user(client)

    assert user.email == 'testuser@example.com'
    assert len(mailoutbox) == 1
    activation_mail = mailoutbox[0]
    assert 'activate' in activation_mail.body
    assert 'http' in activation_mail.body


def test_activation(client, mailoutbox):
    user = _register_user(client)
    assert not user.is_active

    # Get activation link from email
    activation_mail = mailoutbox[0]
    activate_url_pattern = '(?P<url>https?://[^\s]+/activate/[^\s]+)'
    url = re.search(activate_url_pattern, activation_mail.body).group('url')

    response = client.get(url)
    user.refresh_from_db()

    assert user.is_active
    # Test automatic login
    assert response.context['user'].is_authenticated


def _register_user(client):
    res = client.post('/en/auth/register/', {
        'username': 'testuser',
        'password1': 'testpass',
        'password2': 'testpass',
        'email': 'testuser@example.com',
    })
    assert res.status_code == 302
    return User.objects.get(username='testuser')
