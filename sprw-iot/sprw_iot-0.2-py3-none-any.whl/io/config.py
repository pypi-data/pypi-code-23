class Config:
    APP_URL = 'http://dev.sprw.io/'
    SPRWIO_GATEWAY_URL = APP_URL + 'api/gateway/'
    access_token = None
    datetime_format = "%Y-%m-%d %I:%M %p"
    @staticmethod
    def set_access_token(token):
        access_token = token
