# -*- coding:utf-8 -*-
from __init__ import db

class DCP_data(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    source_directory = db.Column(db.String(200))
    target_directory = db.Column(db.String(200))
    copy_result = db.Column(db.String(80))
    copy_err = db.Column(db.String(200))
    check_result = db.Column(db.String(20))
    check_err = db.Column(db.String(200))
    check_hash_result = db.Column(db.String(20))
    check_hash_err = db.Column(db.String(200))

    movie_id = db.Column(db.Integer, db.ForeignKey("movie_data.id"))
    movie = db.relationship("Movie_data", back_populates="dcps")

