#!/usr/bin/env python

import requests
import json
import yaml
from pprint import pprint
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def yaml_load(filename):
    fh = open(filename, "r")
    yamlrawtext = fh.read()
    yamldata = yaml.load(yamlrawtext)
    return yamldata
    
def fdm_login(host,username,password):
    '''
    This is the normal login which will give you a ~30 minute session with no refresh.  
    Should be fine for short lived work.  
    Do not use for sessions that need to last longer than 30 minutes.
    '''
    headers = {
       "Content-Type": "application/json",
       "Accept": "application/json",
       "Authorization":"Bearer"
    }
    payload = {"grant_type": "password", "username": username, "password": password}
    
    request = requests.post("https://{}:{}/api/fdm/v2/fdm/token".format(host, FDM_PORT),
                     json=payload, verify=False, headers=headers)
    if request.status_code == 400:
       raise Exception("Error logging in: {}".format(request.content))
    try:
       access_token = request.json()['access_token']
       return access_token
    except:
       raise

def fdm_get(host,token,url):
    '''
    This is a GET request.
    '''
    headers = {
       "Content-Type": "application/json",
       "Accept": "application/json",
       "Authorization":"Bearer {}".format(token)
    }
    try:

        request = requests.get("https://{}:{}/api/fdm/v2{}?limit=100".format(host, FDM_PORT,url),verify=False, headers=headers)
        return request.json()
    except:
        raise

if __name__ == "__main__":
    #  load FMC IP & credentials here
    ftd_host = {}
    ftd_host = yaml_load("profile_ftd.yml")    
    pprint(ftd_host["devices"])    
    #pprint(fmc_host["devices"][0]['ipaddr'])
    FDM_USER = ftd_host["devices"][0]['username']
    FDM_PASSWORD = ftd_host["devices"][0]['password']
    FDM_HOST = ftd_host["devices"][0]['ipaddr']
    FDM_PORT = ftd_host["devices"][0]['port']
    token = fdm_login(FDM_HOST,FDM_USER,FDM_PASSWORD) 
    print()
    print (" TOKEN :")
    print(token)
    print('======================================================================================================================================')    
    # STEP 1  Get the Policy ID , we need it as the parent ID for accessrules management    
    api_url="/policy/accesspolicies"
    accesspolicy = fdm_get(FDM_HOST,token,api_url)
    #print(json.dumps(accesspolicy,indent=4,sort_keys=True))
    data=accesspolicy['items']
    for entry in data:
       PARENT_ID=entry['id']
    print('PARENT ID ( needed for access policies ) = ')
    print(PARENT_ID)
    print()    
    fa = open("access_policies.txt","w")   
    api_url="/policy/accesspolicies/"+PARENT_ID+"/accessrules"
    access_policies = fdm_get(FDM_HOST,token,api_url)
    print(json.dumps(access_policies,indent=4,sort_keys=True))
    '''
    for line in access_policies['items']:
        print('name:', line['name'])
        print('value:', line['port'])
        print('description:', line['description'])
        print('type:', line['type'])
        print('id:', line['id'])
        print()
        if line['name'].find("EW_TCP")==0:
            fa.write(line['name'])
            fa.write(';')            
            fa.write(line['port'])
            fa.write(';')   
            if line['description']==None:
                line['description']="No Description"
            fa.write(line['description'])
            fa.write(';')            
            fa.write(line['type'])
            fa.write(';')
            fa.write(line['id'])
            fa.write('\r')	
    '''		
    fa.close()          

    
