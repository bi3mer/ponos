from typing import Dict, Any, List
from random import seed
from requests import get
from json import dumps

class Game:
    def __init__(self, server: str, json_data: Dict[str, Any]):
        self.completability_endpoint = f'{server}/completability'

        self.elites_per_bin: int = json_data['elites-per-bin']
        self.iterations: int = json_data['iterations']
        self.max_strand_size: int = json_data['max-strand-size']
        self.n: int = json_data['n']
        self.start_population_size: int = json_data['start-population-size']
        self.start_strand_size: int = json_data['start-strand-size']

        if 'seed' in json_data:
           seed(json_data['seed'])

    def completability(self, level: List[str]) -> float:
        c_request = get(self.completability_endpoint, params={'lvl': dumps(level)})
        if c_request.status_code != 200:
            print(f"'{self.completability_endpoint}' endpoint returned status code: {c_request.status_code}")
            exit(1)

        try:
            c = float(c_request.content)
        except ValueError:
            print(f"Completability response '{c_request.content}' could not be parsed to a float.")
            exit(1)

        assert c >= 0.0, "Completion value must be in the inclusive range of 0 and 1."
        assert c <= 1.0, "Completion value must be in the inclusive range of 0 and 1."

        return c