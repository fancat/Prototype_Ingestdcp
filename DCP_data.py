# -*- coding:utf-8 -*-
from __init__ import db
import os

class DCP_data(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    source_directory = db.Column(db.String(200))
    target_directory = db.Column(db.String(200))
    dcp_name = db.Column(db.String(200))
    copy_result = db.Column(db.String(80))
    copy_err = db.Column(db.String(200))
    check_result = db.Column(db.String(20))
    check_err = db.Column(db.String(200))
    check_warning = db.Column(db.String(200))
    check_hash_result = db.Column(db.String(20))
    check_hash_err = db.Column(db.String(200))
    torrent_directory = db.Column(db.String(200))
    torrent_result = db.Column(db.String(20))
    torrent_err = db.Column(db.String(200))

    movie_id = db.Column(db.Integer, db.ForeignKey("movie_data.id"))
    movie = db.relationship("Movie_data", back_populates="dcps")

    def get_s_dcp_path(self):
        return os.path.join(self.source_directory,self.dcp_name)
    def get_t_dcp_path(self):
        return os.path.join(self.target_directory,self.dcp_name)
    def get_torrent_path(self):
        return os.path.join(self.torrent_directory,self.dcp_name) + ".torrent"