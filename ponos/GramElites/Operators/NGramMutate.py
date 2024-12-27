from random import randrange, random
from typing import List

from Utility.LinkerGeneration import generate_link
from Game import Game
from .IMutate import IMutate


class NGramMutate(IMutate):
    def __init__(self, G: Game):
        self.G = G

    def mutate(self, strand: List[str]) -> List[str]:
        if random() < self.G.mutation_rate:
            point = randrange(self.G.ngram.n - 1, len(strand) - self.G.ngram.n - 1)
            start =  strand[:point]
            end = strand[point + 1:]

            assert self.G.ngram.sequence_is_possible(start)
            assert self.G.ngram.sequence_is_possible(end)

            link = generate_link(self.G, start, end, 1)
            path = start + link + end

            assert self.G.ngram.sequence_is_possible(path)

            return path[:self.G.max_strand_size]

        return strand
