from ast import Index
from genericpath import isdir
#!/usr/bin/env python

from Utility.web import web_get
from GramElites.MapElites import MapElites
from Game import Game

from random import seed
from time import time
import argparse
import shutil
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
    # TODO: handle extension
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
    # level segment generation
    map_elites = MapElites(G)
    map_elites.run()

    # store usable level segments


    # Linking


    # Export as MDP

if __name__ == '__main__':
    start = time()
    main()
    end = time()

    print(f'Time to run: {end - start}')