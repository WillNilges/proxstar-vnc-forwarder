from proxmoxer import ProxmoxAPI
import json
from http import client as httplib
import urllib.parse
import requests

import websockets
import asyncio

import secrets

def connect_proxmox():
    for host in proxmox_hosts:
        try:
            proxmox = ProxmoxAPI(
                host,
                user=proxmox_user,
                password=proxmox_pass,
                verify_ssl=False,
            )
            proxmox.version.get()
            return proxmox
        except:
            if proxmox_hosts.index(host) == (len(proxmox_hosts) - 1):
                print('unable to connect to any of the given Proxmox servers')
                raise

def node(search_id):
    proxmox = connect_proxmox()
    for vm in proxmox.cluster.resources.get(type='vm'):
        if vm['vmid'] == int(search_id):
            return vm['node']
    return None

proxmox_hosts = ['proxmox03-nrh.csh.rit.edu','proxmox01-nrh.csh.rit.edu','proxmox02-nrh.csh.rit.edu']
proxmox_user = secrets.USER
proxmox_pass = secrets.PASS

proxmox = connect_proxmox()

node='proxmox03-nrh'
burger_king_foot_lettuce=urllib.parse.quote_plus('&')
search_id = 131

def try_with_password():
    data = {"username": proxmox_user, "password": proxmox_pass}
    response_data = requests.post(
        "https://proxmox01-nrh.csh.rit.edu:8006/" + "api2/json/access/ticket",
        verify=False,
        data=data,
    ).json()["data"]
    if response_data is None:
        raise AuthenticationError(
            "Could not authenticate against `ticket` endpoint! Check uname/password"
        )

    print(f"response data (tell me ur secrets) {response_data}")

    csrf_prevention_token = response_data['CSRFPreventionToken']
    webbed_csrf_prevention_token = urllib.parse.quote_plus(csrf_prevention_token)
    
    ticket = response_data['ticket']
    webbed_ticket = urllib.parse.quote(ticket)

    # perm = requests.get("https://proxmox01-nrh.csh.rit.edu:8006/api2/json/access/permissions",cookies={"PVEAuthCookie": webbed_ticket})
    # print(f"{perm.status_code} | {perm.text}")

    proxy_params = {"node": node, "vmid": str(search_id), "websocket": '1', "generate-password": '1'}

    vncproxy_response_data = requests.post(
        "https://proxmox03-nrh.csh.rit.edu:8006" + f"/api2/json/nodes/{node}/qemu/{search_id}/vncproxy",
        verify=False,
        params=proxy_params,
        headers={"CSRFPreventionToken": csrf_prevention_token},
        cookies={"PVEAuthCookie": ticket}
    ).json()["data"]
    
    if response_data is None:
        raise AuthenticationError(
            "Could not authenticate against `vncproxy` endpoint!"
        )

    print()
    print(vncproxy_response_data["port"])
    # vnc_ticket = vncproxy_response_data['ticket']
    # vnc_port = vncproxy_response_data['port']
    # vnc_password = vncproxy_response_data['password']
    # webbed_vnc_ticket=urllib.parse.quote_plus(vnc_ticket)



try_with_password()