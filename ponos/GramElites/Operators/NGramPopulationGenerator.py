from typing import List

from itertools import repeat
from random import choice

from .IPopulationGenerator import IPopulationGenerator
from Game import Game

class NGramPopulationGenerator(IPopulationGenerator):
    def __init__(self, G: Game):
        self.G = G

    def generate(self, n: int) -> List[List[str]]:
        keys = list(self.G.ngram.grammar.keys())
        return [
            self.G.ngram.generate(choice(keys), self.G.start_strand_size)
            for _ in repeat(None, n)
        ]
