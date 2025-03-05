from typing import Dict, Any, List

from Utility.web import Client
from Utility.LevelAssessment import LevelAssessment
from Utility.MarkovChain import MarkovChain
from Utility.Metric import Metric
from Utility.Ngram import NGram
from Utility.GridTools import columns_into_rows, rows_into_columns

class Game:
    def __init__(self, client: Client, json_data: Dict[str, Any]):
        self.client = client

        # json data
        self.death_reward: float = json_data['death-reward']
        self.end_reward: float = json_data['end-reward']
        self.elites_per_bin: int = json_data['elites-per-bin']
        self.mutation_rate: float = json_data['mutation-rate']
        self.iterations: int = json_data['iterations']
        self.max_strand_size: int = json_data['max-strand-size']
        self.start_population_size: int = json_data['start-population-size']
        self.start_strand_size: int = json_data['start-strand-size']
        self.ngram_operators: bool = json_data['n-gram-operators']
        self.levels_are_horizontal: bool = json_data['levels-are-horizontal']

        self.metrics: List[Metric] = []
        for m in json_data['computational-metrics']:
            self.metrics.append(Metric(
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

        for lvl in self.client.get_levels():
            if self.levels_are_horizontal:
                lvl = rows_into_columns(lvl)
                self.ngram.add_sequence(lvl)
                unigram.add_sequence(lvl)
            else:
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

        if 'custom-liking-columns' in json_data:
            self.linking_slices: List[List[str]] = json_data['custom-liking-columns']
        else:
            self.linking_slices: List[List[str]] = [[l] for l in unigram_keys if all(c not in l for c in self.structure_chars)]

    def assess(self, level: List[str]) -> LevelAssessment:
        if self.levels_are_horizontal:
            results = self.client.assess(level)
        else:
            results = self.client.assess(columns_into_rows(level))

        metrics = []
        for m in self.metrics:
            value = results[m.name]
            assert value >= 0, f"{m.name} must be >= 0"
            assert value <= 1, f"{m.name} must be <= 1"
            metrics.append(value)

        c = results['completability']
        assert c >= 0.0, "Completion value must be >= 0."
        assert c <= 1.0, "Completion value must be <= 1."

        return LevelAssessment(results['completability'], metrics)

    def reward(self, level: List[str]) -> float:
        if self.levels_are_horizontal:
            return self.client.reward(level)

        return self.client.reward(columns_into_rows(level))