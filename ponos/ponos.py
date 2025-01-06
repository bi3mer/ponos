#!/usr/bin/env python

from typing import List, Tuple, cast

from GramElites.MapElites import MapElites
from GDM.GDM.Graph import Graph

from Utility.Math import euclidean_distance, tuple_add
from Utility.Linking import build_links_between_nodes
from Utility.Link import Link
from Utility.CustomNode import CustomNode
from Utility.CustomEdge import CustomEdge
from Utility.web import web_get
from Game import Game

from random import seed
from time import time
import argparse
import json
import os

def tuple_to_key(tup: Tuple[float,...]) -> str:
    return '_'.join(str(k) for k in tup)

def main():
    # Get arguments from command line
    parser = argparse.ArgumentParser(description='Ponos')
    parser.add_argument('--server', type=str, help="URL, ideally 127.0.0.1:[PORT] for game server.")
    parser.add_argument('--socket', type=str, help="URL for web socket.")
    parser.add_argument(
        '--model-name',
        type=str,
        help="Name of file for resulting pickle file (don't include extension).",
        required=True
    )

    args = parser.parse_args()

    if args.socket == None and args.server == None:
        parser.print_help()
        exit(1)
    elif args.socket != None and args.server != None:
        print('Cannot use both socket and server, please only use one.')
        exit(1)
    elif args.socket:
        print('Web socket not yet supported... :/')
        exit(1)

    server = args.server

    # Make sure file won't be overwritten
    mdl_name = args.model_name
    if os.path.exists(mdl_name + '.json'):
        index = 0
        new_name = f'{mdl_name}_{index}.json'
        while os.path.exists(new_name):
            index += 1
            new_name = f'{mdl_name}_{index}.json'

        mdl_name = new_name
    else:
        mdl_name += '.json'

    print(f'Result will be stored at: {mdl_name}')

    # Get config from game server
    json_config = json.loads(web_get(f'{server}/config'))

    # set seed if relevant
    if 'seed' in json_config:
        seed(json_config['seed'])

    # set up game
    G = Game(server, json_config)

    ####### Gram-Elites
    print('Running MAP-Elites...')
    map_elites = MapElites(G)
    map_elites.run()

    ####### Linking
    level_segments_found = 0

    # Add Nodes and finding start node for linking step
    ORIGIN = tuple(0 for _ in range(len(G.metrics)))
    start_node = None

    dist = 1000000
    print('Adding nodes...')
    BINS = map_elites.bins
    MDP = Graph()
    MDP.add_default_node(node_name="start", terminal=True, reward=0.0)
    MDP.add_default_node(node_name="death", terminal=True, reward=G.death_reward)

    for key in BINS:
        B = BINS[key]
        bin_name = tuple_to_key(key)

        # elite fitness must be 0.0 to be *usable*
        segments: List[List[str]] = [elite[1] for elite in B if elite[0] == 0.0]

        if len(segments) > 0:
            level_segments_found += len(segments)

            MDP.add_node(CustomNode(
                name = bin_name,
                reward = 0,
                utility = 0,
                is_terminal = False,
                neighbors = set(),
                levels = segments
            ))

            D = euclidean_distance(ORIGIN, key)
            if D < dist:
                dist = D
                start_node = key

    print(f'Built {level_segments_found} level segments.')
    assert start_node != None, "No valid start node found."

    # calculate link directions list
    DIRECTIONS = []
    _base_direction = [0 for _ in range(len(G.metrics))]
    for i in range(len(G.metrics)):
        new_direction = _base_direction.copy()
        new_direction[i] = 1
        DIRECTIONS.append(new_direction)

        new_direction = _base_direction.copy()
        new_direction[i] = -1
        DIRECTIONS.append(new_direction)

    # Add edges with no link or link if valid. Otherwise, don't add.
    print('Linking edges...')

    seen = set()
    seen.add(start_node)
    queue = [start_node]

    while len(queue) != 0:
        src = queue.pop()
        src_name = tuple_to_key(src)

        for dir in DIRECTIONS:
            tgt = tuple_add(src, dir)
            tgt_name = tuple_to_key(tgt)

            # If node doesn't exist, go to next direction
            if not MDP.has_node(tgt_name):
                continue

            # create edge
            links = build_links_between_nodes(
                cast(CustomNode, MDP.get_node(src_name)),
                cast(CustomNode, MDP.get_node(tgt_name)),
                G
            )

            if len(links) > 0:
                MDP.add_edge(CustomEdge(
                    src=src_name,
                    tgt=tgt_name,
                    probability=[(tgt_name, 0.99), ("death", 0.01)],
                    links=links # ERROR: not building a link!
                ))

            # add new target to queue if it has not yet been seen
            if tgt not in seen:
                seen.add(tgt)
                queue.append(tgt)

    ####### Store
    print('Storing the result...')
    with open(mdl_name, 'w') as f:
        f.write(MDP.to_json_string())

    print('DONE')

if __name__ == '__main__':
    start = time()
    main()
    end = time()

    print(f'Time to run: {end - start}')