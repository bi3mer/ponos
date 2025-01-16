from typing import Dict, Any, Union, List
from urllib.request import urlopen
from json import loads, dumps
import socket

def web_get(endpoint: str, params: Union[Dict[str, Any], None]=None) -> Any:
    if params != None:
        args = []
        for key in params:
            args.append(f'{key}={dumps(params[key]).replace(" ", "%20")}')

        endpoint += "?" + '&'.join(args)

    with urlopen(endpoint) as R:
        return R.read().decode('utf-8')

def web_get_json(endpoint: str, params: Union[Dict[str, Any], None]=None) -> Any:
    return loads(web_get(endpoint, params))

class Client:
    def get_config(self) -> Dict[str, Any]:
        raise NotImplementedError()

    def get_levels(self):
        raise NotImplementedError()

    def assess(self, lvl: List[str]):
        raise NotImplementedError()

class RestClient(Client):
    def __init__(self, host: str, port: int):
        print("REST")
        self.url = f'{host}:{port}'
        self.assess_endpoint = f'{self.url}/assess'

    def get_config(self) -> Dict[str, Any]:
        return web_get_json(f'{self.url}/config')

    def get_levels(self):
        return web_get_json(f'{self.url}/levels')

    def assess(self, lvl: List[str]):
        return web_get_json(self.assess_endpoint, {'lvl': dumps(lvl)})

class SocketClient(Client):
    def __init__(self, host: str, port: int):
        print("SOCKET")
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))

    def __del__(self):
        self.s.close()

    def get_config(self) -> Dict[str, Any]:
        self.s.sendall(b"config")
        data = self.s.recv(1024)
        return loads(data.decode('utf-8'))

    def get_levels(self):
        self.s.sendall(b"levels")

        lvls = ''
        while 'EOF' not in lvls:
            data = self.s.recv(1024)
            lvls += data.decode('utf-8')

        return loads(lvls[:-3])

    def assess(self, lvl: List[str]):
        print(lvl)
        self.s.sendall(f"assess{dumps(lvl)}".encode('utf-8'))
        data = self.s.recv(1024)
        return loads(data.decode('utf-8'))