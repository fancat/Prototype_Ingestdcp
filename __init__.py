from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_bootstrap import Bootstrap
from flask_nav import Nav

app = Flask(__name__)
app.config.from_object(u"config")
Bootstrap(app)
db = SQLAlchemy(app)
api = Api(app)
nav = Nav()

