# -*- coding:utf-8 -*-
from tdcpblib.tdcpb_checks import tdcpb_check
from requests import post,get
#path = "/home/maeva/Stage/DCP/DJANGO_TLR-G_F_EN-FR_FR_51_2K_SPE_20121020_YMA_OV"
#tdcpb_check(path)
nb_DCP = 1
source_directory = u"/home/maeva/Stage/DCP/DJANGO_TLR-G_F_EN-FR_FR_51_2K_SPE_20121020_YMA_OV"
movie = u"Django Unchained"
data = {u"source_directory":source_directory,u"nb_DCP":nb_DCP,u"movie":movie}
# print(get('http://localhost:5000/dcps/1').json())
# print(post('http://localhost:5000/dcps/', data=data).json())
# print(get('http://localhost:5000/dcps/'))
# print(get('http://localhost:5000/dcps/').json())
headers = {u"Accept":u"application/json",}
r = get(u"http://localhost:5000/dcps/",headers=headers)
print(r.request.headers)
print(r.headers)
print(r)
print(r.json())