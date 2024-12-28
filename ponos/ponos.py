#!/usr/bin/env python

from GramElites.MapElites import MapElites
from GDM.GDM.Graph import Graph

from Utility.Math import euclidean_distance
from Utility.CustomNode import CustomNode
from Utility.CustomEdge import CustomEdge
from Utility.web import web_get
from Game import Game

from random import seed
from time import time
import argparse
import json
import os

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
    if os.path.exists(mdl_name + '.pkl'):
        index = 0
        new_name = f'{mdl_name}_{index}.pkl'
        while os.path.exists(new_name):
            index += 1
            new_name = f'{mdl_name}_{index}'

        mdl_name = new_name
    else:
        mdl_name += '.pkl'

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
    # Add Nodes and finding start node for linking step
    ORIGIN = tuple(0 for _ in range(len(G.metrics)))
    start_node = None

    dist = 1000000
    print('Adding nodes...')
    BINS = map_elites.bins
    MDP = Graph()
    for key in BINS:
        B = BINS[key]
        start_name = '_'.join(str(k) for k in key)
        for i, elite in enumerate(B):
            # elite fitness must be 0.0 to be *usable*
            if elite[0] == 0.0:
                MDP.add_node(CustomNode(
                    name = f'{start_name}_{i}',
                    reward = 0,
                    utility = 0,
                    is_terminal = False,
                    neighbors = set(),
                    level = elite[1]
                ))

                D = euclidean_distance(ORIGIN, key)
                if D < dist:
                    dist = D
                    start_node = key

    print(f'Built {len(MDP.nodes)} level segments.')
    assert start_node != None, "No valid start node found."
    start_node = start_node + (0,)

    # Add edges with no link or link if valid. Otherwise, don't add.
    print('Linking edges...')
    print(f'Start Node {start_node} for level assembly.')
    # if MDP.has_key()


    ####### MDP
    print('Storing result...')
    # Add start node and death node

    # export


    print('DONE')

if __name__ == '__main__':
    start = time()
    main()
    end = time()

    print(f'Time to run: {end - start}')