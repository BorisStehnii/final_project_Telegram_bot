from flask import Flask, session, request
from flask_session import Session
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import telegram as tg


fapp = Flask(__name__)
fapp.config.from_object(Config)
# bot = tg.Bot(token=Config.TBOT_TOKEN)

db = SQLAlchemy(fapp)
migrate = Migrate(fapp, db)

from app import views, models
