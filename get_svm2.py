from netapp_ontap import HostConnection, config
from netapp_ontap.resources import Svm

config.CONNECTION = HostConnection('‌192.168.0.102', username='admin', password='Netapp1!', verify=False)

svm = Svm()

print(svm.name)
