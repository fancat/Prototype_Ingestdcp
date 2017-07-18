# -*- coding:utf-8 -*-
from flask import render_template, request, make_response, Response, jsonify
from flask_restful import Resource, reqparse, fields, marshal_with
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from __init__ import app, db, api
from tdcpblib.common import TdcpbException
from DCP_data import DCP_data
from threads import Check,Copy

db.create_all()

nav = Nav()
@nav.navigation()
def mynavbar():
    return Navbar(u"IngestDCP",View(u"Accueil",u"index"))
nav.register_element(u"top",mynavbar)

@app.route(u"/")
def index():
    return render_template(u"view_skeleton.html")


@api.representation(u"text/html")
def output_html(data,code,headers=None):

    data = data.popitem()
    page = u"{}.html".format(data[0])
    return make_response(render_template(page,data=data[1]), code, headers)

@api.representation(u"application/json")
def output_html(data,code,headers=None):
    data = data.popitem()[1]
    return jsonify(data)

# @app.route("/dcps/")
# def dcps():
#     DCPs = db.session.query(DCP_data).all()
#     return render_template("dcps.html",DCPs=DCPs)

DCP_fields = {
    u"id": fields.Integer,
    u"movie": fields.String,
    u"copy_result": fields.String,
    u"copy_err": fields.String,
    u"check_result": fields.String,
    u"check_err": fields.String,
    u"check_hash_result": fields.String,
    u"check_err": fields.String
}


class DCPList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(u"movie",type=str,help=u"Name of the movie is missing", required=True, location=u"form")
        self.reqparse.add_argument(u"source_directory",type=str,help=u"Path of the directory is missing", required=True, location=u"form")
        super(DCPList, self).__init__()


    def post(self):
        print(request.form)
        data = self.reqparse.parse_args()
        print(data)
        movie = data[u"movie"]
        source_directory = data[u"source_directory"]
        dcp = DCP_data(movie=movie, source_directory=source_directory)
        db.session.add(dcp)
        db.session.commit()

        c = Check(dcp.id)
        c.start()
        return {u"result":u"OK",u"message":u"Le DCP a bien été créé"}

    @marshal_with(DCP_fields,u"dcps")
    def get(self):
        dcps = db.session.query(DCP_data).all()
        return dcps



class DCP(Resource):
    @marshal_with(DCP_fields, u"dcp")
    def get(self, id_dcp):
        dcp = DCP_data.query.filter_by(id=id_dcp).first()
        return dcp

api.add_resource(DCP,u"/dcps/<int:id_dcp>/")
api.add_resource(DCPList,u"/dcps/")

if __name__ == u"__main__":
    nav.init_app(app)
    app.run(debug=True)