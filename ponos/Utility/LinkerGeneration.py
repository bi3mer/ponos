from typing import List, Optional
from collections import deque
from Game import Game

def generate_link(G: Game, start: List[str], end: List[str], min_size: int=0) -> Optional[List[str]]:
    # Make sure input is n-gram generable
    assert G.ngram.sequence_is_possible(start), f'Invalid n-gram sequence: {start}'
    assert G.ngram.sequence_is_possible(end), f'Invalid n-gram sequence: {end}'

    # If no extra columns have to be generated and the combination of start and
    # end is already valid, then return. However, if an agent is given, validate
    # that the agent can play through the combination before returning.
    combined = start + end
    if min_size == 0 and G.ngram.sequence_is_possible(combined):
        assessment = G.assess(combined)
        if assessment.percent_completable == 1.0:
            return []

    del combined

    ######### Build Link
    # generate path of minimum length with an n-gram
    N = G.ngram.n
    min_size += N - 1

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
        current_prior = node[0]
        link_length = node[1]

        # link found, but make sure it is longer than min length
        if current_prior == end_prior and link_length >= min_size:
            # reconstruct path and return
            path = []

            while node != start_node:
                path.append(node[0][-1])
                node = came_from[node]

            path.reverse()
            return path[:1-N]

        # We haven't, so expand the search
        output = G.ngram.get_unweighted_output_list(current_prior)
        if output == None:
            continue

        next_link_length = link_length + 1
        for new_column in output:
            # build the new prior with the slice found by removing the first
            # slice
            new_prior = current_prior[1:] + (new_column,)
            new_node = (new_prior, next_link_length)

            if new_node in came_from:
                continue

            # if the prior is not the end prior, add it to the search queue and
            # continue the search
            came_from[new_node] = node
            queue.append(new_node)

    # No link found
    return None