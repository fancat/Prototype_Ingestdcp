# -*- coding:utf-8 -*-
from __init__ import app, db, api
from flask import render_template, flash, url_for, redirect, request
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from requests import post

class DCPForm(FlaskForm):
    source_directory = StringField(u"Directory",validators=[DataRequired()])
    movie = StringField(u"Movie",validators=[DataRequired()])


@app.route(u"/dcps/new/", methods=[u"GET",u"POST"])
def new():
    form = DCPForm()
    if form.validate_on_submit():
        data = form.data
        del data["csrf_token"]
        request.form = data
        flash(u"DCP accepted",u"success")
        # r = post(url_for("dcps"), data)
        return redirect(url_for("dcps"),code=307)
    return render_template(u"dcps_new.html",form=form)
