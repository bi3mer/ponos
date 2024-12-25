#!/usr/bin/env python

from Game import Game

from requests import get
import argparse
import json

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
    config_request = get(f'{server}/config')

    if config_request.status_code != 200:
        print(f"'{server}/config' endpoint returned status code: {config_request.status_code}")
        exit(1)

    G = Game(server, json.loads(config_request.content))
    lvl = [
        'X-------------',
        'X-------------',
        'X-------------',
        'X-------------',
        'X-------------',
        'X-------------',
        'X-------------',
        'X-------------',
        'X-------------',
    ]
    res = G.completability(lvl)
    print(res)



if __name__ == '__main__':
    main()