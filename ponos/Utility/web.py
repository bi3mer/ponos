from typing import Dict, Any, Union
from urllib.request import urlopen
from json import loads, dumps

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