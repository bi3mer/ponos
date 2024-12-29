class MarkovChain:
    '''
    Used by Linking.py for structure Markov chains
    '''
    def __init__(self, structure_chars, size, backward=False):
        self.filter = lambda row: any(char in row for char in structure_chars)
        self.markov_chain = {}
        self.backward = backward
        self.max_structure_size = size

    def add_sequence(self, sequence):
        queue = []

        if self.backward:
            sequence = reversed(sequence)

        for token in sequence:
            if self.filter(token):
                queue.append(token)

                if len(queue) < self.max_structure_size:
                    continue

            if len(queue) > 1:
                for i in range(1, len(queue)):
                    key = tuple(queue[0:i])

                    if key in self.markov_chain:
                        self.markov_chain[key].append(queue[i:len(queue)])
                    else:
                        self.markov_chain[key] = [queue[i:len(queue)]]

                queue.clear()

    def get_output(self, sequence):
        if not self.backward:
            sequence = reversed(sequence)

        queue = []
        best_prior = None
        for token in sequence:
            if len(queue) > self.max_structure_size:
                break

            if self.backward:
                queue.insert(0, token)
                prior = tuple(queue)
            else:
                queue.append(token)
                prior = tuple(reversed(queue))

            if prior in self.markov_chain:
                best_prior = prior

        if best_prior == None:
            return [[]]
        else:
            return self.markov_chain[best_prior]