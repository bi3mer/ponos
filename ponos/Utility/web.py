from typing_extensions import Dict, Any, Union
from json import loads
from requests import get

def web_get(endpoint: str, params: Union[Dict[str, Any], None]=None) -> Any:
    request = get(endpoint, params=params)

    if request.status_code != 200:
        print(f"'{endpoint}' endpoint returned status code: {request.status_code}")
        exit(1)

    return request.content

def web_get_json(endpoint: str, params: Union[Dict[str, Any], None]=None) -> Any:
    return loads(web_get(endpoint, params))