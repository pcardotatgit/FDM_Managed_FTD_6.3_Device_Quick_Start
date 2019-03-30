#!/usr/bin/env python
import sys
import csv
import requests
import yaml
import json
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


def fdm_create_network(host,token,payload):
    '''
    This is a POST request to create a new network object in FDM.
    '''
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization":"Bearer {}".format(token)
    }
    try:
        request = requests.post("https://{}:{}/api/fdm/v2/object/networks".format(host, FDM_PORT),
                    json=payload, headers=headers, verify=False)
        return request.json()
    except:
        raise
def convert_mask(ip):
    ip=ip.strip()
    liste=[]
    liste=ip.split(" ")
    address=liste[0]
    netmask=liste[1]
    newmask=sum(bin(int(x)).count('1') for x in netmask.split('.'))
    new_adress=address+'/'+str(newmask)
    return(new_adress)
    
def read_csv(file):
    donnees=[]
    with open (file) as csvfile:
        entries = csv.reader(csvfile, delimiter=';')
        for row in entries:
            #print (' print the all row  : ' + row)
            #print ( ' print only some columuns in the rows  : '+row[1]+ ' -> ' + row[2] )    
            row[1]=row[1].lower()
            if row[1]=='host':
                payload = {
                    "name":row[0],
                    "description":"no description",
                    "subType":"HOST",
                    "value":row[2],
                    "type":"networkobject"
                }
            elif row[1]=='fqdn':
                payload = {
                    "name":row[0],
                    "description":"no description",
                    "subType":"FQDN",
                    "value":row[2],
                    "type":"networkobject"
                }			
            else:
                new_adress=convert_mask(row[2])
                payload = {
                    "name":row[0],
                    "description":"no description",
                    "subType":"NETWORK",
                    "value":new_adress,
                    "type":"networkobject"
                }            
            donnees.append(payload)
    return (donnees)
    
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
    
    fa = open("result.html", "w")
    fa.write("<html><body><center><h1>Object List</h1></center><br>")
    fa.write("<table title='Entries' width='100%' cellpadding=0 cellspacing=0 border=1 bgcolor=#FFFFFFb><tbody>")
    fa.write("<tr><td><center><b>Object Name</b></center></td><td><center><b>Object Type</b></center></td><td><center><b>value</b></center></td><td><center><b>Description</b></center></td></tr>")
    list=[]
    list=read_csv("small_host.csv")
    token = fdm_login(FDM_HOST,FDM_USER,FDM_PASSWORD)    
    print('TOKEN = ')
    print(token)
    print('======================================================================================================================================')    
    for objet in list:
        print(objet)    
        fa.write("<tr><td><center>"+objet['name']+"</center></td><td><center>"+objet['subType']+"</center></td><td><center>"+objet['value']+"</center></td><td><center>"+objet['description']+"</center></td></tr>")            
        post_response = fdm_create_network(FDM_HOST,token,objet)
        print(json.dumps(post_response,indent=4,sort_keys=True))
        print('')    
    fa.write("</tbody></table>")
    fa.write("</body></html>")
