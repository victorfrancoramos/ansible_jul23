'''
import requests

url = "https://cluster2.demo.netapp.com/api/svm/svms"

payload = {}
headers = {
  'Authorization': 'Basic YWRtaW46TmV0YXBwMSE='
}

response = requests.request("GET", url, headers=headers, data = payload, verify=False)

print(response.text.encode('utf8'))
'''

from netapp_ontap import HostConnection
from netapp_ontap.resources import Svm

config.CONNECTION = HostConnection('‌192.168.0.102', username='admin', password='Netapp1!', verify=False)

data = {}
svm = Svm(**data)

print(svm)
