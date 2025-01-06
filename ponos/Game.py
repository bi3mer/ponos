from typing import Dict, Any, List
from json import dumps, loads

from Utility.web import web_get, web_get_json
from Utility.LevelAssessment import LevelAssessment
from Utility.MarkovChain import MarkovChain
from Utility.Metric import Metric
from Utility.Ngram import NGram

class Game:
    def __init__(self, server: str, json_data: Dict[str, Any]):
        # assign server end points
        self.completability_endpoint = f'{server}/completability'
        self.assess_endpoint = f'{server}/assess-level'

        # json data
        self.death_reward: float = json_data['death-reward']
        self.elites_per_bin: int = json_data['elites-per-bin']
        self.mutation_rate: float = json_data['mutation-rate']
        self.iterations: int = json_data['iterations']
        self.max_strand_size: int = json_data['max-strand-size']
        self.start_population_size: int = json_data['start-population-size']
        self.start_strand_size: int = json_data['start-strand-size']
        self.ngram_operators: bool = json_data['n-gram-operators']

        self.metrics: List[Metric] = []
        for m in json_data['computational-metrics']:
            self.metrics.append(Metric(
                min=m['min'],
                max=m['max'],
                resolution=m['resolution'],
                name = m['name']
            ))

        # set up n-grams and markov chains
        self.forward_chain: MarkovChain = MarkovChain(
            json_data['structure-chars'],
            json_data['structure-size'])

        self.backward_chain: MarkovChain = MarkovChain(
            json_data['structure-chars'],
            json_data['structure-size'],
            backward=True)

        self.ngram: NGram = NGram(json_data['n'])
        unigram = NGram(1)

        for lvl in loads(web_get(f'{server}/levels')):
            self.ngram.add_sequence(lvl)
            unigram.add_sequence(lvl)

        unigram_keys = set(unigram.grammar[()].keys())
        pruned = self.ngram.fully_connect()    # remove dead ends from grammar
        unigram_keys.difference_update(pruned) # remove any n-gram dead ends from unigram

        self.mutation_values = list(unigram_keys)

        # set up for linking
        self.allow_empty_link: bool = json_data['allow-empty-link']
        self.max_linker_length: int = json_data['max-linker-length']
        self.structure_chars: List[str] = json_data['structure-chars']

        print('TODO: add support for custom-linking-columns in json_data.')
        if 'custom-liking-columns' in json_data:
            print("custom linking columns not supported yet.")
            self.linking_slices: List[List[str]] = []
            exit(1)
        else:
            self.linking_slices: List[List[str]] = [[l] for l in unigram_keys if all(c not in l for c in self.structure_chars)]

    def assess(self, level: List[str]) -> LevelAssessment:
        results = web_get_json(self.assess_endpoint, {'lvl': dumps(level)})

        metrics = []
        for m in self.metrics:
            value = results[m.name]
            assert value >= m.min, f"Metric must be >= to reported min in config, {m.min}"
            assert value <= m.max, f"Metric must be <= to reported min in config, {m.max}"
            metrics.append(value)

        c = results['completability']
        assert c >= 0.0, "Completion value must be in the inclusive range of 0 and 1."
        assert c <= 1.0, "Completion value must be in the inclusive range of 0 and 1."

        return LevelAssessment(results['completability'], metrics)