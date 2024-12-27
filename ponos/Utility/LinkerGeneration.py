from typing import List, Optional
from collections import deque
from Game import Game

def generate_link(G: Game, start: List[str],end: List[str]) -> Optional[List[str]]:
    '''
    Build a link between two connecting segments. If an agent and feature descriptors
    are provided then this will exhaustively search all possible links and use the
    one with the lowest rmse between the feature values found and the targets based
    on the start and end level segments provided in the arguments.
    '''
    # Make sure input is n-gram generable
    assert G.ngram.sequence_is_possible(start), f'Invalid n-gram sequence: {start}'
    assert G.ngram.sequence_is_possible(end), f'Invalid n-gram sequence: {end}'

    # If no extra columns have to be generated and the combination of start and
    # end is already valid, then return. However, if an agent is given, validate
    # that the agent can play through the combination before returning.
    combined = start + end
    if G.ngram_link_min_length == 0 and G.ngram.sequence_is_possible(combined):
        assessment = G.assess(combined)
        if assessment.percent_completable == 1.0:
            return []

    del combined

    ######### Build Link
    # generate path of minimum length with an n-gram
    N = G.ngram.n

    # BFS to find the ending prior
    queue = deque()
    came_from = {}

    start_node = (tuple(start[-(N - 1):]), 0)
    end_prior = tuple(end[:N - 1])
    queue.append(start_node)
    path = None

    # loop through queue until a path is found
    while queue:
        node = queue.popleft()
        if node[1] + 1 > G.max_strand_size:
            continue

        current_prior = node[0]
        output = G.ngram.get_unweighted_output_list(current_prior)
        if output == None:
            continue

        for new_column in output:
            # build the new prior with the slice found by removing the first
            # slice
            new_prior = current_prior[1:] + (new_column,)
            new_node = (new_prior, node[1] + 1)

            if new_node[1] < G.ngram_link_min_length or new_node in came_from:
                continue

            # if the prior is not the end prior, add it to the search queue and
            # continue the search
            came_from[new_node] = node
            queue.append(new_node)
            if new_prior != end_prior:
                continue

            # link found, reconstruct path
            path = []
            temp_node = new_node
            while temp_node != start_node:
                path.insert(0, temp_node[0][-1])
                temp_node = came_from[temp_node]

            # only use the path if we have constructed a path that is larger than n.
            if len(path) >= G.ngram_link_max_length:
                return path[:-(N - 1)]

    # No link found
    return None