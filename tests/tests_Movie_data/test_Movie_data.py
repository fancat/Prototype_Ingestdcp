# -*- coding:utf-8 -*-
import unittest
from flask_testing import TestCase
from flask import Flask
from __init__ import db
from DCP_data import DCP_data
from Movie_data import Movie_data
from datetime import datetime

class TestMovie_data(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config[u"SQLALCHEMY_DATABASE_URI"] = u"sqlite://"
        app.config[u"TESTING"] = True
        app.config[u"SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        db.init_app(app)
        return app

    def setUp(self):
        db.create_all()

        self.dcp1 = DCP_data()
        self.dcp2 = DCP_data()
        self.list_dcps = [self.dcp1, self.dcp2]

    def test_db(self):
        self.assertIsNotNone(db)

    def test_db_empty(self):
        self.assertEqual(db.session.query(DCP_data).all(),[])
        self.assertEqual(db.session.query(Movie_data).all(),[])

    def test_addMovie(self):
        movie = Movie_data()
        db.session.add(movie)
        db.session.commit()
        self.assertEqual(movie.id, 1)
        self.assertListEqual(movie.dcps,[])
        self.assertIsNone(movie.release_date)
        self.assertIsNone(movie.description)
        self.assertIsNone(movie.category)

    def test_addMovie2(self):
        movie = Movie_data()
        db.session.add(movie)
        db.session.commit()
        movie_q = db.session.query(Movie_data).first()
        self.assertEqual(movie_q.id, 1)
        self.assertListEqual(movie.dcps,[])
        self.assertIsNone(movie.release_date)
        self.assertIsNone(movie.description)
        self.assertIsNone(movie.category)

    def test_dcps(self):
        movie = Movie_data(dcps=self.list_dcps)
        db.session.add(movie)
        db.session.commit()
        movie_q = db.session.query(Movie_data).first()
        self.assertIsInstance(movie_q.dcps, list)
        self.assertItemsEqual(map(type,movie_q.dcps), [DCP_data]*len(movie_q.dcps))

    def test_dcps2(self):
        movie = Movie_data()
        db.session.add(movie)
        movie.dcps.append(self.dcp1)
        movie.dcps.append(self.dcp2)
        db.session.commit()
        movie_q = db.session.query(Movie_data).first()
        self.assertItemsEqual(movie_q.dcps, self.list_dcps)

    def test_release_date(self):
        date = datetime.today()
        movie = Movie_data(release_date=date)
        db.session.add(movie)
        db.session.commit()
        movie_q = db.session.query(Movie_data).first()
        self.assertIsInstance(movie.release_date, datetime)

    def test_description(self):
        movie = Movie_data(description=u"desc")
        db.session.add(movie)
        db.session.commit()
        movie_q = db.session.query(Movie_data).first()
        self.assertIsInstance(movie.description, unicode)

    def test_category(self):
        movie = Movie_data(category=u"long")
        db.session.add(movie)
        db.session.commit()
        movie_q = db.session.query(Movie_data).first()
        self.assertIn(movie.category,["long","court","trailer"])

    def test_title(self):
        movie = Movie_data(title=u"tl")
        db.session.add(movie)
        db.session.commit()
        movie_q = db.session.query(Movie_data).first()
        self.assertIsInstance(movie.title, unicode)

    def original_title(self):
        movie = Movie_data(original_title=u"otl")
        db.session.add(movie)
        db.session.commit()
        movie_q = db.session.query(Movie_data).first()
        self.assertIsInstance(movie.original_title, unicode)


    def tearDown(self):
        db.session.remove()
        db.drop_all()

if __name__ == "__main__":
    unittest.main()