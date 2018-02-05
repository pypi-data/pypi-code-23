from connection import api_post


def init_storage(app, user):
    return api_post('/app/init_storage', data={"app_name": app, "user_name": user})
