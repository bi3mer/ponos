from typing import List, Optional
from collections import deque

from ponos.Game import Game

'''
Citation: Biemer, C., & Cooper, S. (2022, August). On Linking Level Segments. In 2022 IEEE Conference on Games (CoG) (pp. 199-205).
Original repository: https://github.com/bi3mer/LinkingLevelSegments/tree/main
'''

def concatenate_link(start: List[str], end: List[str], G: Game) -> Optional[List[str]]:
    return [] if G.assess(start + end).percent_completable == 1.0 else None

def tree_search_link(start: List[str], end: List[str], G: Game) -> Optional[List[str]]:
    '''
    This is very similar to the code in Linker Generation. The main difference is that we
    are testing searchig for something that is 100% playable
    '''
    if G.allow_empty_link and \
       G.ngram.sequence_is_possible(start + end) and \
       G.assess(start + end).percent_completable == 1.0:
        return []

    for START_LINK in G.forward_chain.get_output(start):
        for END_LINK in G.backward_chain.get_output(end):
            END_LINK = list(reversed(END_LINK))

            if G.allow_empty_link and \
                G.assess(start + START_LINK + END_LINK + end).percent_completable == 1.0:
                return START_LINK + END_LINK

            queue = deque([o for o in G.linking_slices])

            while len(queue) > 0:
                current_path = queue.popleft()
                NEW_LEVEL = start + START_LINK + current_path + END_LINK + end

                if G.assess(NEW_LEVEL).percent_completable == 1.0:
                    assert G.ngram.sequence_is_possible(NEW_LEVEL)
                    return START_LINK + current_path + END_LINK

                if len(current_path) < G.max_linker_length:
                    for o in G.linking_slices:
                        queue.append(current_path + o)

    return None