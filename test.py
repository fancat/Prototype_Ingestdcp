# -*- coding:utf-8 -*-
from tdcpblib.tdcpb_checks import tdcpb_check
from requests import post,get
#path = "/home/maeva/Stage/DCP/DJANGO_TLR-G_F_EN-FR_FR_51_2K_SPE_20121020_YMA_OV"
#tdcpb_check(path)
source_directory = u"/home/maeva/Stage/DCP/DJANGO_TLR-G_F_EN-FR_FR_51_2K_SPE_20121020_YMA_OV"
movie = u"Django Unchained"
data = {u"source_directory":source_directory,u"movie":movie}
# print(get('http://localhost:5000/dcps/1').json())
print(post(u"http://localhost:5000/dcps/", data=data))
# print(get('http://localhost:5000/dcps/'))
# print(get('http://localhost:5000/dcps/').json())
# headers = {"Accept":"application/json; q=1.0, text/html; q=0.5, */*; q=0.1",}
# r = get('http://localhost:5000/dcps/',headers=headers)
# print(r.request.headers)
# print(r.json())