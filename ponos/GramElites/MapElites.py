from random import sample
from math import floor
from heapq import heappush

from Utility.ProgressBar import update_progress
from GramElites.Operators.IMutate import IMutate
from GramElites.Operators.ICrossover import ICrossover
from GramElites.Operators.NGramCrossover import NGramCrossover
from GramElites.Operators.NGramMutate import NGramMutate
from GramElites.Operators.NGramPopulationGenerator import NGramPopulationGenerator
from Game import Game

class MapElites:
    '''
    This is the more basic form of map-elites without resolution switching,
    parallel execution, etc.
    '''
    def __init__(self, G: Game):
        if G.ngram_operators:
            self.crossover: ICrossover = NGramCrossover(G)
            self.mutate: IMutate = NGramMutate(G)
            self.population_generator = NGramPopulationGenerator(G)
        else:
            print('Non n-gram operators not supported right now...')
            exit(1)
            # self.crossover: ICrossover = Operators.SinglePointCrossover(G)
            # self.mutate: Operators.IMutate = Operators.Mutate(G)
            # self.population_generator: IPopulationGenerator =  Operators.RandomPopulationGenerator(G)

        self.G: Game = G
        self.bins = {}

    def run(self):
        self.bins = {}
        self.keys = set()

        ###### Population Generation
        print('Level Generation: population generation...')
        update_progress(0)
        for i, strand in enumerate(self.population_generator.generate(self.G.start_population_size)):
            self.__add_to_bins(strand)
            update_progress(i / self.G.start_population_size)
        update_progress(1)

        ###### Run Map-Elites
        print('Level Generation: segment optimization...')
        update_progress(0)
        LEN = self.G.iterations
        for i in range(LEN):
            parent_1 = sample(self.bins[sample(self.keys, 1)[0]], 1)[0][1]
            parent_2 = sample(self.bins[sample(self.keys, 1)[0]], 1)[0][1]

            for strand in self.crossover.operate(parent_1, parent_2):
                self.__add_to_bins(self.mutate.operate(strand))
                update_progress(i / LEN)

        update_progress(1)

    def __add_to_bins(self, strand):
        # Get assessment and calculate fitness
        assessment = self.G.assess(strand)
        fitness = self.G.ngram.count_bad_n_grams(strand) + 1 - assessment.percent_completable

        # Calculate the feature vector based on computational metrics
        feature_vector = [0] * len(assessment.metrics)
        for i in range(len(assessment.metrics)):
            M = self.G.metrics[i]
            score_in_range = (assessment.metrics[i] - M.min) * 100 / (M.max - M.min)
            feature_vector[i] = floor(score_in_range / M.resolution)

        # Convert feature vector to tuple and use as a key into the bins dictionary
        feature_vector = tuple(feature_vector)
        if feature_vector not in self.bins:
            self.keys.add(feature_vector)
            self.bins[feature_vector] = [(fitness, strand)]
        else:
            heappush(self.bins[feature_vector], (fitness, strand))
            if len(self.bins[feature_vector]) >= self.G.elites_per_bin:
                self.bins[feature_vector].pop() # only minimize performance
