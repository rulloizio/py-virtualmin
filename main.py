import requests, re, configparser
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def getDomainInformation(host,cfg):
    host_dict= {}
    url = "https://{}:{}/virtual-server/remote.cgi".format(host,cfg.get(host,'PORT'))
    headers = {
    'user-agent': "Script-Py",
    }
    querystring = {"program":"list-domains","json":"1"}
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
    return host_dict
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
    print (re.split(r'(\w+\s?\w+:\s)',results['output']))
    
pass

cfg = configparser.ConfigParser()
cfg.read('config.ini')


for host in cfg.sections():
    # FIXME OK da passare a GOOGLE ! 
    # host_dict= getDomainInformation(host,cfg)
    # TODO
    getServerInformation(host,cfg)
    #print(host_dict)
