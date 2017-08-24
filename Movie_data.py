# -*- coding:utf-8 -*-
from __init__ import db

class Movie_data(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(80))
    original_title = db.Column(db.String(80))
    release_date = db.Column(db.Date)
    description = db.Column(db.Text)
    category = db.Column(db.String(10))

    dcps = db.relationship("DCP_data", back_populates="movie")

