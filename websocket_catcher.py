from proxmoxer import ProxmoxAPI
import json
from http import client as httplib
import urllib.parse
import requests

import websockets
import asyncio
import subprocess

import secrets
import time

from selenium import webdriver
browser = webdriver.Chrome()

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

def main():
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
    csrf_prevention_token = response_data['CSRFPreventionToken']
    webbed_csrf_prevention_token = urllib.parse.quote_plus(csrf_prevention_token)
    
    ticket = response_data['ticket']
    webbed_ticket = urllib.parse.quote(ticket)

    proxy_params = {"node": node, "vmid": str(search_id), "websocket": '1', "generate-password": '0'}

    vncproxy_response_data = requests.post(
        "https://proxmox01-nrh.csh.rit.edu:8006" + f"/api2/json/nodes/{node}/qemu/{search_id}/vncproxy",
        verify=False,
        timeout=5,
        params=proxy_params,
        headers={"CSRFPreventionToken": csrf_prevention_token},
        cookies={"PVEAuthCookie": ticket}
    ).json()["data"]

    print("\nVNCPROXY\n")

    vnc_ticket = vncproxy_response_data['ticket']
    vnc_port = vncproxy_response_data['port']
    webbed_vnc_ticket=urllib.parse.quote_plus(vnc_ticket)

    print(f"Port: {vnc_port}\nTICKET\n{vnc_ticket}")

    if response_data is None:
        raise AuthenticationError(
            "Could not authenticate against `vncproxy` endpoint!"
        )

    # TODO: Find a way to kill after a few hours, to clean up proxies.
    # Or use websockify file.
    novnc_proxy = subprocess.Popen(["/Users/willard.nilges/Code/novnc/utils/novnc_proxy", "--vnc", f"proxmox01-nrh.csh.rit.edu:{vnc_port}"])

    time.sleep(3)

    browser.get(f"http://localhost:6080/vnc.html?host=localhost&port=6080&autoconnect=true&password={webbed_vnc_ticket}")

if __name__ == '__main__':
    main()