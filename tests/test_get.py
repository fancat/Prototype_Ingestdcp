# -*- coding:utf-8 -*-
from requests import get
headers = {u"Accept":u"application/json"}
r = get(u"http://localhost:5000/dcp/1")
print(r)