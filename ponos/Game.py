from typing import Dict, Any, List
from random import seed
from requests import get
from json import dumps, loads

from Utility import NGram

class Game:
    def __init__(self, server: str, json_data: Dict[str, Any]):
        self.completability_endpoint = f'{server}/completability'

        self.elites_per_bin: int = json_data['elites-per-bin']
        self.iterations: int = json_data['iterations']
        self.max_strand_size: int = json_data['max-strand-size']
        self.start_population_size: int = json_data['start-population-size']
        self.start_strand_size: int = json_data['start-strand-size']

        self.ngram: NGram = NGram(json_data['n'])
        unigram = NGram(1)

        level_request = get(f'{server}/levels')
        if level_request.status_code != 200:
            print(f"'{server}/levels' endpoint returned status code: {level_request.status_code}")
            exit(1)

        for lvl in loads(level_request.content):
            self.ngram.add_sequence(lvl)
            unigram.add_sequence(lvl)

        unigram_keys = set(unigram.grammar[()].keys())
        pruned = self.ngram.fully_connect()    # remove dead ends from grammar
        unigram_keys.difference_update(pruned) # remove any n-gram dead ends from unigram

        self.mutation_values = list(unigram_keys)

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