from random import sample
from functools import reduce
from math import floor
from heapq import heappush

from Utility.ProgressBar import update_progress
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
            # self.mutate: Operators.IMutate = Operators.NGramMutate(G)
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
        counts = []
        self.current_count = 0

        self.bins = {}
        self.keys = set()

        update_progress(0)
        for i, strand in enumerate(self.population_generator.generate(self.G.start_population_size)):
            self.__add_to_bins(strand)
            update_progress(i / self.G.start_population_size)
            counts.append(self.current_count)

        update_progress(0)
        for i in range(self.G.iterations):
            parent_1 = sample(self.bins[sample(self.keys, 1)[0]], 1)[0][1]
            parent_2 = sample(self.bins[sample(self.keys, 1)[0]], 1)[0][1]

            for strand in self.crossover(parent_1, parent_2):
                self.__add_to_bins(self.mutator(strand))
                update_progress(i / iterations)

            counts.append(self.current_count)

        update_progress(1)

        return counts

    def __add_to_bins(self, strand):
        '''
        Resolution is the number of bins for each feature. Meaning if we have 2
        features and a resolution of 2, we we will have a 2x2 matrix. We have to
        get scores and map them to the indexes of the matrix. We get this by first
        dividing 100 by the resolution which will be used to get an index
        for a mapping of a minimum of 0 and a max of 100. We are given a min and
        max for each dimension of the user. We take the given score and convert it
        from their mappings to a min of 0 and 100. We then use that and divide the
        result by the 100/resolution to get a float. When we floor it, we get a valid
        index given a valid minimum and maximum from the user.

        Added extra functionality to allow for additional fitness if the main fitness
        is found to be equal to the current best fitness
        '''
        if strand == None:
            return

        # Get assessment and calculate fitness
        assessment = self.G.assess(strand)
        fitness = self.G.ngram.count_bad_n_grams(strand) + 1 - assessment.percent_completable

        # Calculate the feature vector based on computational metrics
        feature_vector = [0] * len(assessment.metrics)
        for i in range(len(assessment.metrics)):
            D = self.G.metrics[i]
            min = D['min']
            max = D['max']
            score_in_range = (assessment.metrics[i] - min) * 100 / (max - min)
            feature_vector[i] = floor(score_in_range / D['resolution'])

        # Convert feature vector to tuple and use as a key into the bins dictionary
        feature_vector = tuple(feature_vector)
        if feature_vector not in self.bins:
            self.keys.add(feature_vector)
            self.bins[feature_vector] = [(fitness, strand)]

            if fitness == 0.0:
                self.current_count += 1
        else:
            current_length = self.__iterator_size((filter(lambda entry: entry[0] == 0.0, self.bins[feature_vector])))
            heappush(self.bins[feature_vector], (fitness, strand))
            if len(self.bins[feature_vector]) >= self.G.elites_per_bin:
                self.bins[feature_vector].pop() # only minimize performance

            new_length = self.__iterator_size(filter(lambda entry: entry[0] == 0.0, self.bins[feature_vector]))
            self.current_count += new_length - current_length

    def __iterator_size(self, iterator):
        return reduce(lambda sum, element: sum + 1, iterator, 0)
