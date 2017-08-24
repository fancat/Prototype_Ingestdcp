# -*- coding:utf-8 -*-
from requests import put
target_directory = u"Nouveau chemin"
movie_id = 3
dcp_name = u"DCP_test"
data = {u"target_directory":target_directory, u"movie_id":movie_id, u"dcp_name":dcp_name}
print(put(u"http://localhost:5000/dcps/1/", data=data).json())