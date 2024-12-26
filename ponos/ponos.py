#!/usr/bin/env python

from Game import Game
from Utility.web import web_get

from random import seed
import argparse
import json

from GramElites import MapElites

def get_cmd_args() -> argparse.Namespace:
    '''
    Build arg parser used to get command line arguments from the user
    '''
    parser = argparse.ArgumentParser(description='Ponos')
    parser.add_argument('--server', type=str, required=True, help="URL for game server.")

    return parser.parse_args()

def main():
    args = get_cmd_args()

    server = args.server

    # Get config
    json_config = json.loads(web_get(f'{server}/config'))

    # set seed if relevant
    if 'seed' in json_config:
        seed(json_config['seed'])

    # set up game
    G = Game(server, json_config)

    lvl = [
        'X-------------',
        'X-------------',
        'X-------------',
        'XE------------',
        'X-------------',
        'XX------------',
        'X-------------',
        'X-------------',
        'X-------------',
        'X-------------',
    ]

    print(G.computational_metrics(lvl))


    # Gram-Elites
    # map_elites = MapElites(
    #     G.start_population_size,

    # )

    # Linking


    # Export as MDP

if __name__ == '__main__':
    main()