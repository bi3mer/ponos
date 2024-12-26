from typing import List
from random import randrange

from Utility.LinkerGeneration import generate_link
from .ICrossover import ICrossover
from Game import Game

class NGramCrossover(ICrossover):
    def __init__(self, G):
        self.G: Game = G

    def operate(self, parent_1: List[str], parent_2: List[str]):
        # get crossover point based on strand lengths. Note that there must be
        # at least n-1 columns on either side for a valid prior to be built.
        strand_size = min(len(parent_1), len(parent_2))
        cross_over_point = randrange(self.G.ngram.n - 1, strand_size - self.G.ngram.n - 1)

        # Built first level. This operation assumes we are working with a fully-
        # connected n-gram. Otherwise, BFS is not guranteed to find a path between
        # two random but valid priors.
        start: List[str] = parent_1[:cross_over_point]
        end: List[str] = parent_2[cross_over_point:]

        assert self.G.ngram.sequence_is_possible(start)
        assert self.G.ngram.sequence_is_possible(end)

        p_1 = start + generate_link(self.G, start, end) + end
        assert self.G.ngram.sequence_is_possible(p_1)

        # build second level
        start = parent_2[:cross_over_point]
        end = parent_1[cross_over_point:]

        assert self.G.ngram.sequence_is_possible(start)
        assert self.G.gram.sequence_is_possible(end)

        p_2 = start + generate_link(self.gram, start, end) + end

        assert self.G.ngram.sequence_is_possible(p_2)

        # return truncated results
        return p_1[:self.max_length], p_2[:self.max_length]
