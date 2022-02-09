import os

base_dir = os.path.abspath(os.path.dirname(__file__))


class Config:
    APP_URL = 'https://tele-api-bot.herokuapp.com/'
    # TBOT_TOKEN = '5168274150:AAEnhdfjtRsLLBwgfx3LBRpMVEM3QanUWvI'
    TBOT_TOKEN = '5182264082:AAFAbEUyjXZJk-hX9kVJRiNw964_2xiS3pU'

    SQLALCHEMY_DATABASE_URI = f'sqlite:///{base_dir}/wmclient.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False







