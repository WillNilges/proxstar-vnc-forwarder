# proxstar-vnc-forwarder
A proof-of-concept way to forward a VNC websocket from proxmox to an unauthenticated PVE user

![image](https://user-images.githubusercontent.com/42927786/177199389-2fd2470a-468d-415d-91d2-5b6675f65deb.png)

## Running
To run do the following

1. Fill out `secrets.py`

`cp secrets_example.py secrets.py`

Add the `api@pve` user's username and password.

2. make a `venv` and activate it

`python3 -m venv venv/`

`source venv/bin/activate`

3. Install requirements 

`pip install -r requirements.txt`

`brew install chromedriver`

4. Run the program

`python websocket_catcher.py`

5. Marvel in the POWER!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
![image](https://user-images.githubusercontent.com/42927786/177910999-f10b4413-093f-47b9-aa53-e781dc7d7da1.png)
