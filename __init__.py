from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_bootstrap import Bootstrap
from flask_nav import Nav
import logging.handlers

app = Flask(__name__)
app.config.from_object(u"config")
Bootstrap(app)
db = SQLAlchemy(app)
api = Api(app, catch_all_404s=True)
nav = Nav()

LOGFILE = u"/Donnees/logs/tdcpb.log"

def create_logger():
    logger = logging.getLogger(u"Api_Ingest_DCP")
    logger.setLevel(logging.INFO)
    fh = logging.handlers.TimedRotatingFileHandler(LOGFILE, when=u"midnight")
    formatter = logging.Formatter(u"%(levelname)s %(asctime)s %(message)s # %(filename)s %(funcName)s l %(lineno)d")
    fh.setFormatter(formatter)
    fh.setLevel(logging.INFO)
    logger.addHandler(fh)
    return logger

logger = create_logger()
