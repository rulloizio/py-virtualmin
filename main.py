import re, configparser,json
from pathlib import Path, PurePath
import requests 
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning

## PARAMETRI
configDir = 'personal_data'
virtualmin_ini_file = 'virtualmin.ini'

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
    ret = []
    url = "https://{}:{}/virtual-server/remote.cgi".format(host,cfg.get(host,'PORT'))
    headers = {
    'user-agent': 'Script-Py',
    }
    querystring = {"program":"info","json":"1","multiline":''}
    try:
        response = requests.request("GET", url, headers=headers, params=querystring, verify=False, auth=HTTPBasicAuth(cfg.get(host,'USR'),cfg.get(host,'PSW')))
        results = response.json()
        with open('personal_data/{}.json'.format(host), 'w') as f:
            json.dump(results, f)
        print ("Connessione a {}: {}  ".format(host,results['status']))
        ret.extend((results['status'],''))
    except requests.exceptions.Timeout as e:
    # Maybe set up for a retry, or continue in a retry loop
        ret.extend(('error',"Timeout: {} {}".format(host, e)))
    except requests.exceptions.TooManyRedirects as e:
        # Tell the user their URL was bad and try a different one
        return ('error',"TooManyRedirects: {} {}".format(host, e))
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        ret.extend(('error',"RequestException: {} {}".format(host, e)))
    except requests.exceptions.ConnectionError() as e:
        # catastrophic error. bail.
        print("ERRORE ConnectionError: {} {}".format(host, e))
        ret.extend( ('error',"ConnectionError: {} {}".format(host, e)))
        #raise SystemExit(e)
   
    return ret
    # TODO: capire come spiittare per PROPRIETA - valore del response
    # print(results['output'].split('\n'))
    # TODO in lavorazione
    #print (re.split(r'(\w+\s?\w+:\s)',results['output']))
    
pass

def main():
    c = Path(PurePath.joinpath(Path.cwd(),configDir,virtualmin_ini_file))
    PurePath.joinpath
    if(not c.exists or not c.is_file):
        c.mkdir(c.cwd())
        c.touch()

    cfg = configparser.ConfigParser()
    cfg.read(c)

    host_dict = []
    # ciclo verifica server
    for host in cfg.sections():
        stato,details = getServerInformation(host,cfg)
        host_dict.append(dict({'Server':host,'stato':stato,'deatils':details}))
        # TODO
    # print(host_dict)    
    # FIXME OK da passare a GOOGLE ! 
    for host in ( x for x in host_dict if x.get('stato')=='success' ):
        host['siti'] = getDomainInformation(host.get('Server'),cfg)
        #host_dict[host['Server']].append(getDomainInformation(host.get('Server'),cfg))
        pass

    with open('personal_data/lista_siti.json', 'w') as f:
        json.dump(host_dict, f)

if __name__ == "__main__":
    main()