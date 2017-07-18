# -*- coding:utf-8 -*-
import unittest
from flask_testing import TestCase
from flask import Flask
from __init__ import db, app
from DCP_data import DCP_data
from Movie_data import Movie_data

class TestDCP_data(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config[u"SQLALCHEMY_DATABASE_URI"] = u"sqlite://"
        app.config[u"TESTING"] = True
        app.config[u"SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        db.init_app(app)
        return app

    def setUp(self):
        db.create_all()

        self.mv = Movie_data()

    def test_db(self):
        self.assertIsNotNone(db)

    def test_db_empty(self):
        self.assertEqual(db.session.query(DCP_data).all(),[])
        self.assertEqual(db.session.query(Movie_data).all(),[])

    def test_addDCP(self):
        dcp = DCP_data()
        db.session.add(dcp)
        db.session.commit()
        self.assertEqual(dcp.id, 1)
        self.assertIsNone(dcp.movie)
        self.assertIsNone(dcp.source_directory)
        self.assertIsNone(dcp.target_directory)

    def test_addDCP2(self):
        dcp = DCP_data()
        db.session.add(dcp)
        db.session.commit()
        dcp_q = db.session.query(DCP_data).first()
        self.assertEqual(dcp_q.id, 1)
        self.assertIsNone(dcp_q.movie)
        self.assertIsNone(dcp_q.source_directory)
        self.assertIsNone(dcp_q.target_directory)

    def test_movie(self):
        dcp = DCP_data(movie=self.mv)
        db.session.add(dcp)
        db.session.commit()
        dcp_q = db.session.query(DCP_data).first()
        self.assertIsInstance(dcp_q.movie, Movie_data)

    def test_source_directory(self):
        dcp = DCP_data(source_directory=u"sd")
        db.session.add(dcp)
        db.session.commit()
        dcp_q = db.session.query(DCP_data).first()
        self.assertIsInstance(dcp_q.source_directory,unicode)

    def test_target_directory(self):
        dcp = DCP_data(target_directory=u"td")
        db.session.add(dcp)
        db.session.commit()
        dcp_q = db.session.query(DCP_data).first()
        self.assertIsInstance(dcp_q.target_directory,unicode)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

if __name__ == "__main__":
    unittest.main()