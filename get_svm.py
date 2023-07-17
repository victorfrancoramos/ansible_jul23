import requests

url = "https://cluster2.demo.netapp.com/api/svm/svms"

payload = {}
headers = {
  'Authorization': 'Basic YWRtaW46TmV0YXBwMSE='
}

response = requests.request("GET", url, headers=headers, data = payload, verify=False)

print(response.text.encode('utf8'))
