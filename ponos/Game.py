from typing import Dict, Any, List
from json import dumps, loads

from Utility.web import web_get, web_get_json

from Utility import NGram

class Game:
    def __init__(self, server: str, json_data: Dict[str, Any]):
        # assign server end points
        self.completability_endpoint = f'{server}/completability'
        self.metrics_endpoint = f'{server}/computational-metrics'

        # json data
        self.elites_per_bin: int = json_data['elites-per-bin']
        self.iterations: int = json_data['iterations']
        self.max_strand_size: int = json_data['max-strand-size']
        self.start_population_size: int = json_data['start-population-size']
        self.start_strand_size: int = json_data['start-strand-size']
        self.metrics = json_data['computational-metrics']

        # set up n-grams
        self.ngram: NGram = NGram(json_data['n'])
        unigram = NGram(1)

        for lvl in loads(web_get(f'{server}/levels')):
            self.ngram.add_sequence(lvl)
            unigram.add_sequence(lvl)

        unigram_keys = set(unigram.grammar[()].keys())
        pruned = self.ngram.fully_connect()    # remove dead ends from grammar
        unigram_keys.difference_update(pruned) # remove any n-gram dead ends from unigram

        self.mutation_values = list(unigram_keys)

    def computational_metrics(self, level: List[str]) -> List[float]:
        metrics = []
        results = web_get_json(self.metrics_endpoint, {'lvl': dumps(level)})
        for m in self.metrics:
            value = results[m['name']]
            assert value >= m['min'], f"Metric must be >= to reported min in config, {m['min']}"
            assert value <= m['max'], f"Metric must be <= to reported min in config, {m['max']}"
            metrics.append(value)

        return metrics

    def completability(self, level: List[str]) -> float:
        try:
            response = web_get(self.completability_endpoint, {'lvl': dumps(level)})
            c = float(response)
        except ValueError:
            print(f"Completability response '{response}' could not be parsed to a float.")
            exit(1)

        assert c >= 0.0, "Completion value must be in the inclusive range of 0 and 1."
        assert c <= 1.0, "Completion value must be in the inclusive range of 0 and 1."

        return c