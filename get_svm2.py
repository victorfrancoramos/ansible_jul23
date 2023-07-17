from netapp_ontap import HostConnection, config
from netapp_ontap.resources import Svm

config.CONNECTION = HostConnection('‌192.168.0.102', username='admin', password='Netapp1!', verify=False)

try:
    for svm in Svm.get_collection(fields="uuid"):
        svm.get()
        print(svm.name)
        print(svm.uuid)
        #print("SVM name:-%s ; SVM uuid:-%s " % (svm.name, svm.uuid))
