# -*- coding:utf-8 -*-
from tdcpblib.tdcpb_checks import tdcpb_check
from requests import post,get
source_dcp_path = u"/Donnees/DCP/DJANGO_TLR-G_F_EN-FR_FR_51_2K_SPE_20121020_YMA_OV"
movie = u"Django Unchained"
movie_category = u"Other"
movie_date = u"1999/05/20"
data = {u"source_dcp_path":source_dcp_path,u"movie_title":movie, u"movie_category":movie_category, u"movie_date":movie_date, u"is_new_movie":u"true"}

rep = post(u"http://localhost:5000/dcps/", data=data)
print(rep.json())