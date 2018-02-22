class Config:
    APP_URL = 'https://sproboticworks.com/'
    SPRWIO_GATEWAY_URL = APP_URL + 'api/iot/gateway/'
    access_token = None
    datetime_format = "%Y-%m-%d %I:%M %p"
    @staticmethod
    def set_access_token(token):
        access_token = token
