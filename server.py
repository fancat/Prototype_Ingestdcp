# -*- coding:utf-8 -*-
from flask import render_template, request, make_response, Response, jsonify, redirect, flash, send_file, url_for
from flask_restful import Resource, reqparse, fields, marshal_with, marshal, abort
from flask_nav.elements import Navbar, View
from __init__ import app, db, api, nav
from DCP_data import DCP_data
from Movie_data import Movie_data
from threads import Check, CreateTorrent, HashCheck, Copy, PATH_TORRENTS
from form_new_dcp import new
from form_edit_dcp import edit
# from autocompletion import movies_autocomp
import os
import datetime



@nav.navigation()
def mynavbar():
    return Navbar(u"IngestDCP",View(u"Dcps",u"dcps"),View(u"Movies",u"movies"))
nav.register_element(u"top",mynavbar)



@api.representation(u"text/html")
def output_html(data,code,headers=None):
    if code == 400:
        flash(data[u"message"],u"danger")
        arguments = data.copy()
        del arguments[u"message"]
        del arguments[u"html_page"]
        return redirect(url_for(data[u"html_page"], **arguments))
    data = data.popitem()
    page = u"{}.html".format(data[0])
    if type(data[1]) != list:
        flash(data[1][u"message"], u"success")
    return make_response(render_template(page,data=data[1]), code, headers)

@api.representation(u"application/json")
def output_json(data,code,headers=None):
    data = data.popitem()[1]
    return make_response(jsonify(data), code, headers)

class DateField(fields.Raw):
    def format(self, value):
        if value:
            return value.strftime("%Y-%m-%d")
        return None

DCP_fields_light = {
    u"id": fields.Integer,
    u"dcp_name": fields.String,
}
movie_fields_light = {
    u"id": fields.Integer,
    u"title": fields.String,
    u"release_date": DateField
}
movie_fields = {
    u"id": fields.Integer,
    u"title": fields.String,
    u"original_title": fields.String,
    u"release_date": DateField,
    u"description": fields.String,
    u"category": fields.String,
    u"dcps": fields.List(fields.Nested(DCP_fields_light))
}
DCP_fields = {
    u"id": fields.Integer,
    u"movie": fields.Nested(movie_fields_light),
    u"dcp_name": fields.String,
    u"source_directory": fields.String,
    u"target_directory": fields.String,
    u"copy_result": fields.String,
    u"copy_err": fields.String,
    u"check_result": fields.String,
    u"check_err": fields.String,
    u"check_hash_result": fields.String,
    u"check_hash_err": fields.String,
    u"torrent_result": fields.String,
    u"torrent_err": fields.String,
    u"message": fields.String
}




class DCPList(Resource):
    def __init__(self):
        # Making POST args
        # To create base attributes of DCP
        self.reqparse_base = reqparse.RequestParser()
        self.reqparse_base.add_argument(u"source_dcp_path",type=str, help=u"Path of the DCP is missing", required=True, location=u"form")
        self.reqparse_base.add_argument(u"is_new_movie", type=str, help=u"The string is_new_movie is missing", required=True, location=u"form")

        # To select a existing movie
        self.reqparse_select = reqparse.RequestParser()
        self.reqparse_select.add_argument(u"movie_id", type=int, help=u"The movie id is not valid", required=True, location=u"form")

        # To create a new movie
        self.reqparse_new = reqparse.RequestParser()
        self.reqparse_new.add_argument(u"source_dcp_path",type=str, help=u"Path of the DCP is missing", required=True, location=u"form")
        self.reqparse_new.add_argument(u"movie_title", type=str, required=True, location=u"form")
        self.reqparse_new.add_argument(u"movie_original_title", type=str, location=u"form")
        self.reqparse_new.add_argument(u"movie_date", type=str, help=u"Release date is missing", required=True, location=u"form")
        self.reqparse_new.add_argument(u"movie_category", type=str, help=u"Category is missing", required=True, location=u"form")
        super(DCPList, self).__init__()


    # POST : Create a dcp
    @marshal_with(DCP_fields,u"dcp")
    def post(self):
        data = self.reqparse_base.parse_args()
        source_directory = os.path.dirname(data[u"source_dcp_path"])
        dcp_name = os.path.basename(data[u"source_dcp_path"])
        if not dcp_name:
            abort(400, message=u"DCP can't be unnamed", html_page=u"dcps")
        if data[u"is_new_movie"] == u"true":
            # If we make a new movie
            data = self.reqparse_new.parse_args()
            movie = Movie_data()
            movie.title = data[u"movie_title"]
            movie.original_title = data[u"movie_original_title"]
            if data[u"movie_date"]:
                try:
                    movie.release_date = datetime.datetime.strptime(data[u"movie_date"],u"%Y-%m-%d")
                except ValueError:
                    abort(400, message=u"Release date not well formatted (must match 'yyyy-mm-dd')", html_page=u"dcps")
            if data[u"movie_category"] in [u"Long", u"Short", u"Trailer"]:
                movie.category = data[u"movie_category"]
            else:
                abort(400, message=u"Category is not valid (must be 'Long', 'Short' or 'Trailer')", html_page=u"dcps")
        else:
            # If we select an existing movie
            data = self.reqparse_select.parse_args()
            movie = db.session.query(Movie_data).filter_by(id=data[u"movie_id"]).first()
            if not movie:
                abort(400, message=u"Movie with id={} does no longer exist", html_page=u"dcps")
        dcp = DCP_data(movie=movie, source_directory=source_directory, dcp_name=dcp_name)
        db.session.add(dcp)
        db.session.commit()

        c = Check(dcp.id)
        c.start()

        dcp.message = u"DCP created"
        return dcp

    # GET : View all dcps
    # @marshal_with(DCP_fields,u"dcps")
    def get(self):
        dcps = db.session.query(DCP_data).all()
        return marshal(dcps, DCP_fields, envelope=u"dcps"), 200



class DCP(Resource):
    def __init__(self):
        self.reqparse_edit = reqparse.RequestParser()
        self.reqparse_edit.add_argument(u"dcp_name",type=str, location=u"form")
        self.reqparse_edit.add_argument(u"source_directory",type=str, location=u"form")
        self.reqparse_edit.add_argument(u"target_directory", type=str, location=u"form")
        self.reqparse_edit.add_argument(u"movie_id", type=int, help=u"movie_id is not an int", location=u"form")

        self.reqparse_edit.add_argument(u"check", type=str, location=u"form")
        super(DCP, self).__init__()

    # GET : View a dcp
    @marshal_with(DCP_fields, u"dcp")
    def get(self, id_dcp):
        dcp = DCP_data.query.filter_by(id=id_dcp).first()
        return dcp

    # PUT : Edit a dcp
    @marshal_with(DCP_fields,u"dcp")
    def put(self, id_dcp):
        dcp = DCP_data.query.filter_by(id=id_dcp).first()
        data = self.reqparse_edit.parse_args(strict=True)
        if data.get(u"movie_id"):
            movie = db.session.query(Movie_data).filter_by(id=data[u"movie_id"]).first()
            if not movie:
                abort(400, message=u"Movie with id={} does not exist".format(data.get(u"movie_id")), html_page=u"dcp", id_dcp=id_dcp)
            dcp.movie = movie
            del data[u"movie_id"]
        # Assign all remaining attrib
        for arg, val in data.items():
            if val:
                dcp.__setattr__(arg,val)

        # Reexecute checks
        if data.get(u"check"):
            if data[u"check"] == u"create_torrent":
                ct = CreateTorrent(id_dcp)
                ct.start()
            elif data[u"check"] == u"short_check":
                sc = Check(id_dcp, False)
                sc.start()
            elif data[u"check"] == u"hash_check":
                ht = HashCheck(id_dcp, False)
                ht.start()
            elif data[u"check"] == u"copy":
                cp = Copy(id_dcp, False)
                cp.start()
            else:
                abort(400, message=u"Check is not valid (must be: 'copy', 'short_check', 'hash_check' or 'create_torrent')", html_page=u"dcp", id_dcp=id_dcp)

        db.session.commit()
        return dcp

    # DELETE : Remove a dcp
    @marshal_with(DCP_fields,u"dcps")
    def delete(self, id_dcp):
        dcp = db.session.query(DCP_data).filter_by(id=id_dcp).first()
        if not dcp:
            abort(400, message=u"DCP with id={} does not exist".format(id_dcp), html_page=u"dcps")
        name = dcp.dcp_name
        db.session.delete(dcp)
        db.session.commit()
        dcps = db.session.query(DCP_data).all()
        return dcps


class MovieList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(u"title", type=str, help=u"Title is missing", required=True, location=u"form")
        self.reqparse.add_argument(u"original_title", type=str, location=u"form")
        self.reqparse.add_argument(u"release_date", type=str, help=u"Release date is missing", required=True, location=u"form")
        self.reqparse.add_argument(u"description", type=str, location=u"form")
        self.reqparse.add_argument(u"category", type=str, help=u"Category is missing", required=True, location=u"form")
        self.reqparse.add_argument(u"dcps_id", type=int, help=u"dcps_id must be ints", action=u"append", location=u"form")
        super(MovieList, self).__init__()

    # GET : View all movies
    @marshal_with(movie_fields, u"movies")
    def get(self):
        movies = db.session.query(Movie_data).all()
        return movies

    # POST : Create a movie
    @marshal_with(movie_fields, u"movies")
    def post(self):
        data = self.reqparse.parse_args()
        movie = Movie_data()
        movie.title = data[u"title"]
        movie.original_title = data.get(u"movie_original_title")
        if data.get(u"release_date"):
            try:
                movie.release_date = datetime.datetime.strptime(data[u"release_date"],u"%Y-%m-%d")
            except ValueError:
                abort(400, message=u"Release date not well formatted (must match 'yyyy-mm-dd')", html_page=u"dcps")
        if data[u"category"] in [u"Long", u"Short", u"Trailer"]:
            movie.category = data[u"category"]
        else:
            abort(400, message=u"Category is not valid (must be: 'Long', 'Short' or 'Trailer')", html_page=u"dcps")
        if data.get(u"dcps_id"):
            for dcp_id in data.get(u"dcps_id"):
                dcp = db.session.query(DCP_data).filter_by(id=dcp_id).first()
                if not dcp:
                    abort(400, message=u"DCP with id={} does not exist".format(dcp_id), html_page=u"dcps")
                movie.dcps.append(dcp)
        db.session.commit()
        movies = db.session.query(Movie_data).all()
        return movies


class Movie(Resource):
    def __init__(self):
        self.reqparse_edit = reqparse.RequestParser()
        self.reqparse_edit.add_argument(u"title",type=str, location=u"form")
        self.reqparse_edit.add_argument(u"movie_title",type=str, location=u"form")
        self.reqparse_edit.add_argument(u"release_date", type=str, location=u"form")
        self.reqparse_edit.add_argument(u"description", type=str, location=u"form")
        self.reqparse_edit.add_argument(u"add_dcp", type=int, help=u"add_dcp is not an int", location=u"form")
        self.reqparse_edit.add_argument(u"remove_dcp", type=int, help=u"remove_dcp is not an int", location=u"form")
        super(Movie, self).__init__()

    # GET : View a movie
    @marshal_with(movie_fields, u"movie")
    def get(self, id_movie):
        movie = Movie_data.query.filter_by(id=id_movie).first()
        return movie

    #PUT : Edit a movie
    @marshal_with(movie_fields, u"movie")
    def put(self, id_movie):
        movie = db.seesion.query(Movie_data).filter_by(id=id_movie).first()
        data = self.reqparse_edit.parse_args(strict=True)
        if data.get(u"add_dcp"):
            dcp = db.session.query(DCP_data).filter_by(id=data[u"add_dcp"]).first()
            if not dcp:
                abort(400, message=u"DCP with id={} does not exist".format(data.get(u"add_dcp")), html_page=u"movie", id_movie=id_movie)
            movie.dcp.append(dcp)
            del data[u"add_dcp"]
        if data.get(u"remove_dcp"):
            dcp = db.session.query(DCP_data).filter_by(id=data[u"remove_dcp"]).first()
            if not dcp:
                abort(400, message=u"DCP with id={} does not exist".format(data.get(u"remove_dcp")), html_page=u"movie", id_movie=id_movie)
            movie.dcp.remove(dcp)
            del data[u"remove_dcp"]
        if data.get(u"release_date"):
            try:
                movie.release_date = datetime.datetime.strptime(data[u"movie_date"], u"%Y-%m-%d")
            except ValueError:
                abort(400, message=u"Release date not well formatted (must match 'yyyy-mm-dd')", html_page=u"movie", id_movie=id_movie)
            del data[u"release_date"]
        # Assign all remaining attrib
        for arg, val in data.items():
            if val:
                movie.__setattr__(arg, val)
        db.session.commit()
        return movie

    # DELETE : Remove a movie
    @marshal_with(movie_fields, u"movies")
    def delete(self, id_movie):
        movie = db.session.query(DCP_data).filter_by(id=id_movie).first()
        if not movie:
            abort(400, message=u"Movie with id={} does not exist".format(id_movie), html_page=u"movies")
        title = movie.title
        db.session.delete(title)
        db.session.commit()
        dcps = db.session.query(Movie_data).all()
        return dcps


@app.route(u"/")
def index():
    return redirect(u"dcps")

@app.route(u"/dcps/<id_dcp>/torrent/")
def download_torrent(id_dcp):
    dcp = db.session.query(DCP_data).filter_by(id=id_dcp).first()
    path = dcp.get_torrent_path()
    if not path:
        flash(u"Torrent directory does not exist for DCP {}".format(dcp.dcp_name), u"danger")
        abort(404, message=u"The torrent file doesn't exist yet for this DCP")
    elif not os.path.isfile(path):
        flash(u"Torrent {} does not exist".format(path), u"danger")
        abort(404, message=u"The torrent file doesn't exist yet for this DCP")
    else:  # si le fichier existe
        return send_file(path, as_attachment=True)  # on l'envoie

def main(testing=False):
    api.add_resource(DCP,u"/dcps/<int:id_dcp>/", endpoint="dcp")
    api.add_resource(DCPList,u"/dcps/", endpoint="dcps")
    api.add_resource(MovieList,u"/movies/", endpoint="movies")
    api.add_resource(Movie,u"/movies/<int:id_movie>/", endpoint="movie")
    nav.init_app(app)
    if testing:
        app.config[u"SQLALCHEMY_DATABASE_URI"]=u"sqlite:///:memory:"
        db.init_app(app)
    db.create_all()
    app.run(debug=True,threaded=True)

if __name__ == u"__main__":
    main()