#!/usr/bin/env python

from Utility.web import web_get
from GramElites.MapElites import MapElites
from Game import Game

from random import seed
from time import time
import argparse
import json

def main():
    # Get server from user input
    parser = argparse.ArgumentParser(description='Ponos')
    parser.add_argument('--server', type=str, required=True, help="URL for game server.")
    args = parser.parse_args()

    server = args.server

    # Get config from game server
    json_config = json.loads(web_get(f'{server}/config'))

    # set seed if relevant
    if 'seed' in json_config:
        seed(json_config['seed'])

    # set up game
    G = Game(server, json_config)

    # Gram-Elites level segment generation
    map_elites = MapElites(G)
    map_elites.run()

    # Linking


    # Export as MDP

if __name__ == '__main__':
    start = time()
    main()
    end = time()

    print(f'Time to run: {end - start}')