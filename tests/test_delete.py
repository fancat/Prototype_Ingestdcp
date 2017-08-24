# -*- coding:utf-8 -*-
from requests import delete
d = delete(u"http://localhost:5000/dcps/3/")
print(d)