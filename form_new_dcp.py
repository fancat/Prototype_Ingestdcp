# -*- coding:utf-8 -*-
from __init__ import app, db, api
from flask import render_template, flash, url_for, redirect, request
from flask_wtf import FlaskForm
from wtforms import SelectField,StringField, HiddenField, FileField
from wtforms.validators import DataRequired
from Movie_data import Movie_data
import inspect

class DCPForm(FlaskForm):
    source_dcp_path = StringField(u"DCP path")
    # movie = StringField(u"Movie",validators=[DataRequired()])
    movie_id = SelectField(u"Movie", coerce=int)
    is_new_movie = HiddenField(id=u"is_new_movie",default = u"false")
    movie_title = StringField(u"Title")
    movie_original_title = StringField(u"Original title")
    movie_date = StringField(u"Release date")
    movie_category = SelectField(u"Category", choices=[(u"Long",u"Long"),(u"Short",u"Short"),(u"Trailer",u"Trailer")])



@app.route(u"/dcps/new/", methods=[u"GET",u"POST"])
def new():
    form = DCPForm(request.form)
    movies = db.session.query(Movie_data).all()
    form.movie_id.choices = [(m.id, m.title) for m in movies]
    if request.method == u"POST":
        # print(inspect.getmembers(form, predicate=inspect.ismethod))
        if form.data[u"is_new_movie"]:
            form.data[u"is_new_movie"] = u"true"
        else:
            form.data[u"is_new_movie"] = u"false"
        flash(u"DCP accepted",u"success")
        return redirect(url_for(u"dcps"),code=307)

    return render_template(u"dcps_new.html",form=form)

