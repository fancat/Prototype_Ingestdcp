# -*- coding:utf-8 -*-
import unittest
from flask_testing import TestCase
from flask import Flask
from __init__ import db
from DCP_data import DCP_data
from Movie_data import Movie_data
from tdcpblib.tdcpb_checks import tdcpb_check
from requests import post,get
import threading
import server

class TestServer(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config[u"SQLALCHEMY_DATABASE_URI"] = u"sqlite://"
        app.config[u"TESTING"] = True
        app.config[u"SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        db.init_app(app)
        return app

    def setUp(self):
        db.create_all()
        self.source_directory = u"/home/maeva/Stage/DCP/DJANGO_TLR-G_F_EN-FR_FR_51_2K_SPE_20121020_YMA_OV"
        movie = u"Django Unchained"
        self.data = {u"source_directory": self.source_directory, u"movie": movie}
        self.server_url = u"http://localhost:5000"
        post(self.server_url + u"/dcps/", data=self.data)

    def test_db(self):
        self.assertIsNotNone(db)

    def test_db_empty(self):
        self.assertEqual(db.session.query(DCP_data).all(),[])
        self.assertEqual(db.session.query(Movie_data).all(),[])


    def test_server_run(self):
        r = get(self.server_url)


    def test_source_directory(self):
        tdcpb_check(self.source_directory)

    def test_DCPs_get(self):
        r = get(self.server_url + u"/dcps/")
        self.assertEqual(r.headers[u"Content-Type"],u"application/json")

    def test_DCP_get_json(self):
        headers = {u"Accept":u"application/json"}
        r = get(self.server_url + u"/dcps/", headers=headers)
        self.assertEqual(r.headers[u"Content-Type"],u"application/json")

    def test_DCP_get_html(self):
        headers = {u"Accept":u"text/html"}
        r = get(self.server_url + u"/dcps/", headers=headers)
        self.assertRegexpMatches(r.headers[u"Content-Type"],r"^text/html*")

    def test_DCP_post(self):
        headers = {u"Accept":u"application/json"}
        post(self.server_url + u"/dcps/", data=self.data)
        r = get(self.server_url + u"/dcps/",headers=headers).json()
        # print([e["source_directory"] for e in r])
        print r
        self.assertEqual(r[1][u"source_directory"],self.data[u"source_directory"])
        self.assertEqual(r[1][u"movie"][u"title"],self.data[u"movie"])

    def tearDown(self):
        db.session.remove()
        db.drop_all()

if __name__ == u"__main__":
    unittest.main()