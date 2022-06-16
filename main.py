import requests, re, configparser,json
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def getDomainInformation(host,cfg):
    siti = []
    url = "https://{}:{}/virtual-server/remote.cgi".format(host,cfg.get(host,'PORT'))
    headers = {
    'user-agent': "Script-Py",
    }
    querystring = {"program":"list-domains","json":"1"}
    response = requests.request("GET", url, headers=headers, params=querystring, verify=False, auth=HTTPBasicAuth(cfg.get(host,'USR'),cfg.get(host,'PSW')))
    results = response.json()
    for row in results['data']:
        reg_exp = re.compile(r'(?P<dominio>[\w\.]+)(\s\s+)(?P<username>[\w]+)')
        split_string = reg_exp.match(row['name'])
        #split_string = re.split("( ){2,}", row['name'])
        if (split_string and not split_string.group('dominio')=='Domain'):
            siti.append(dict({'Dominio':split_string.group('dominio'), 'Username':split_string.group('username')}))
    return siti
pass

def getServerInformation(host,cfg):
    url = "https://{}:{}/virtual-server/remote.cgi".format(host,cfg.get(host,'PORT'))
    headers = {
    'user-agent': 'Script-Py',
    }
    querystring = {"program":"info","json":"1"}
    response = requests.request("GET", url, headers=headers, params=querystring, verify=False, auth=HTTPBasicAuth(cfg.get(host,'USR'),cfg.get(host,'PSW')))
    results = response.json()
   
    print ("Connessione a {}: {}  ".format(host,results['status']))
    # TODO: capire come spiittare per PROPRIETA - valore del response
    # print(results['output'].split('\n'))
    # TODO iin lavorazione
    #print (re.split(r'(\w+\s?\w+:\s)',results['output']))
    
pass

cfg = configparser.ConfigParser()
cfg.read('personal_data/config.ini')

host_dict = []
# ciclo verifica server
for host in cfg.sections():
    host_dict.append(dict({'Server':host}))
    # TODO
    getServerInformation(host,cfg)
print(host_dict)    
# FIXME OK da passare a GOOGLE ! 
for host in host_dict:
    host['siti'] = getDomainInformation(host.get('Server'),cfg)
    #host_dict[host['Server']].append(getDomainInformation(host.get('Server'),cfg))

with open('personal_data/lista_siti.json', 'w') as f:
    json.dump(host_dict, f)
