import requests, re, configparser
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

cfg = configparser.ConfigParser()
cfg.read('config.ini')

for host in cfg.sections():
    host_dict= {}
    url = "https://{}:{}/virtual-server/remote.cgi".format(host,cfg.get(host,'PORT'))
    querystring = {"program":"list-domains","json":"1"}
    headers = {
    'user-agent': "Script-Py",
    }
    # print(url)
    response = requests.request("GET", url, headers=headers, params=querystring, verify=False, auth=HTTPBasicAuth(cfg.get(host,'USR'),cfg.get(host,'PSW')))
    results = response.json()
    print ("Connessione a {}: {}  ".format(host,results['status']))
    for row in results['data']:
        reg_exp = re.compile(r'(?P<dominio>[\w\.]+)(\s\s+)(?P<username>[\w]+)')
        split_string = reg_exp.match(row['name'])
        #split_string = re.split("( ){2,}", row['name'])
        if (split_string and not split_string.group('dominio')=='Domain'):
            #print("{} - {}".format(split_string.group('dominio'),split_string.group('username')))
            host_dict.setdefault(host,[]).append({'Dominio':split_string.group('dominio'), 'Username':split_string.group('username')})
    print(host_dict)
