#!/usr/bin/env python

from typing import List, Tuple, cast

from GramElites.MapElites import MapElites
from GDM.GDM.utility import bfs
from GDM.GDM.Graph import Graph

from Utility.ProgressBar import progress_text, update_progress
from Utility.Math import manhattan_distance, tuple_add, mean
from Utility.Linking import  tree_search_link
from Utility.CustomNode import CustomNode
from Utility.CustomEdge import CustomEdge
from Utility.GridTools import columns_into_rows
from Utility.web import RestClient, SocketClient
from Game import Game

from random import seed
from time import time
import argparse
import os

def tuple_to_key(tup: Tuple[float,...]) -> str:
    return '_'.join(str(k) for k in tup)

def main():
    ###########################################################################
    # Get arguments from command line
    parser = argparse.ArgumentParser(description='Ponos')
    parser.add_argument(
        '--host',
        type=str,
        default="127.0.0.1",
        help="URL for host, defaults to 127.0.0.1",
    )

    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help="URL for host, defaults to 8000",
    )

    parser.add_argument(
        '--use-rest-server',
        default=False,
        action='store_true',
        help="Set to true if the server uses REST instead of a socket. Default is to use a socket."
    )

    parser.add_argument(
        '--model-name',
        type=str,
        help="Name of file for resulting pickle file (don't include extension).",
        required=True
    )

    args = parser.parse_args()

    ###########################################################################
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

    ###########################################################################
    # Get config from game server
    if args.use_rest_server:
        client = RestClient(f'http://{args.host}', args.port)
    else:
        client = SocketClient(args.host, args.port)

    json_config = client.get_config()

    # set seed if relevant
    if 'seed' in json_config:
        seed(json_config['seed'])

    # set up game
    G = Game(client, json_config)

    ###########################################################################
    # Run Gram-Elites
    print('Running MAP-Elites...')
    map_elites = MapElites(G)
    map_elites.run()

    ###########################################################################
    # Build nodes and find the node that should be connected to the start node
    level_segments_found = 0

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

        # elite fitness must be 0.0 to be usable, and we don't want duplicate
        # elite level segments
        segments: List[List[str]] = []
        for elite in B:
            if elite[0] == 0.0 and elite[1] not in segments:
                segments.append(elite[1])

        level_segments_found += len(segments)
        for i in range(len(segments)):

            MDP.add_node(CustomNode(
                name = f"{bin_name}-{i}",
                reward = -1, # assigned later
                utility = 0, # assigned later
                is_terminal = False,
                neighbors = set(),
                level = segments[i],
                depth = -1   # assigned later
            ))

            D = manhattan_distance(ORIGIN, key)
            if D < dist:
                dist = D
                start_node = key

    print(f'Built {level_segments_found} level segments.')
    assert start_node != None, "No valid start node found. This means no usable nodes were found, and the search failed."

    ###########################################################################
    # Calculate link directions list
    POSITIVE_DIRECTIONS = []
    NEGATIVE_DIRECTIONS = []
    _base_direction = [0 for _ in range(len(G.metrics))]
    for i in range(len(G.metrics)):
        new_direction = _base_direction.copy()
        new_direction[i] = 1
        POSITIVE_DIRECTIONS.append(new_direction)

        new_direction = _base_direction.copy()
        new_direction[i] = -1
        NEGATIVE_DIRECTIONS.append(new_direction)

    ###########################################################################
    # Find every possible link
    print('Linking edges...')
    seen = set()
    seen.add(start_node)
    queue = [start_node]
    possible_links: List[Tuple[str, str]] = []

    while len(queue) != 0:
        progress_text(f'Possible links: {len(possible_links)}')
        src = queue.pop()

        src_names = []
        for i in range(G.elites_per_bin):
            name = f"{tuple_to_key(src)}-{i}"
            if name in MDP.nodes:
                src_names.append(name)
            else:
                break

        assert len(src_names) > 0

        found = False
        for dir in POSITIVE_DIRECTIONS:
            tgt = src
            for _ in range(40): # TODO: this is bad, should be smarter
                tgt = tuple_add(tgt, dir)
                tgt_name = tuple_to_key(tgt)

                should_break = False
                for i in range(G.elites_per_bin):
                    tgt_name = f"{tgt_name}-{i}"

                    if MDP.has_node(tgt_name):
                        should_break = True
                        found = True
                        for src_name in src_names:
                            possible_links.append((src_name, tgt_name))

                        # add new target to queue if it has not yet been seen
                        if tgt not in seen:
                            seen.add(tgt)
                            queue.append(tgt)
                            break

                if should_break:
                    break

        # If there is no possible path forward, then try in a negative direction
        # to save the work already done
        if found:
            continue

        # duplicate code, but convenient
        for dir in NEGATIVE_DIRECTIONS:
            tgt = src
            for _ in range(40): # TODO: this is bad, should be smarter
                tgt = tuple_add(tgt, dir)
                tgt_name = tuple_to_key(tgt)

                should_break = False
                for i in range(G.elites_per_bin):
                    tgt_name = f"{tgt_name}-{i}"

                    if MDP.has_node(tgt_name):
                        should_break = True
                        found = True
                        for src_name in src_names:
                            possible_links.append((src_name, tgt_name))

                        # add new target to queue if it has not yet been seen
                        if tgt not in seen:
                            seen.add(tgt)
                            queue.append(tgt)
                            break

                if should_break:
                    break


    progress_text(f'Possible links: {len(possible_links)}', done=True)

    ###########################################################################
    # Run linking. Note, a better implementation would use some threading so
    # with multiple ports to the server
    success_links = 0
    total = 0

    for i, (src_name, tgt_name) in enumerate(possible_links):
        progress_text(f'Links made: {success_links}/{total}')
        total += 1
        src_node = cast(CustomNode, MDP.get_node(src_name))
        tgt_node = cast(CustomNode, MDP.get_node(tgt_name))

        # Try to create a link
        link = tree_search_link(src_node.level, tgt_node.level, G)
        if link == None:
            continue # failed keep going

        # otherwise, success and make the link
        success_links += 1
        MDP.add_edge(CustomEdge(
            src=src_name,
            tgt=tgt_name,
            probability=[(tgt_name, 0.99), ("death", 0.01)],
            link=link
        ))


    progress_text(f'Links made: {success_links}/{total}', done=True)

    ###########################################################################
    # Find node with lowest sum of BCs and make it connect to start node
    min_dist = 10000000
    min_dist_node_name = ""

    for node_name in MDP.nodes:
        if "start" in node_name or "death" in node_name or "end" in node_name:
            continue

        dist = sum(int(b) for b in node_name.split('-')[0].split('_'))

        if dist < min_dist:
            min_dist = dist
            min_dist_node_name = node_name

    # edge from start node to minimum distance node
    MDP.add_edge(CustomEdge(
        src="start",
        tgt=min_dist_node_name,
        probability=[(min_dist_node_name, 0.99), ("death", 0.01)],
        link=[]
    ))

    ###########################################################################
    # Remove any node that is not connected to the start node
    nodes_removed = 0
    removing_nodes = True
    nodes = list(MDP.nodes.keys())
    nodes.remove("start")
    nodes.remove("death")

    while removing_nodes:
        removing_nodes = False
        for node_name in nodes:
            path = bfs(MDP, "start", node_name)
            if path == None:
                nodes_removed += 1
                removing_nodes = True

                MDP.remove_node(node_name)
                nodes.remove(node_name)
                break

    print(f"Nodes without a path to start: {nodes_removed}")
    print(f"Nodes left: {len(MDP.nodes)}")

    ###########################################################################
    # Find the node(s) furthest from the start node
    max_depth = 0
    max_depth_node_names = []

    seen = set()
    seen.add("start")
    queue = [("start", 0)]

    while len(queue) > 0:
        node_name, depth = queue.pop(0)
        new_depth = depth + 1

        for neighbor in MDP.neighbors(node_name):
            if neighbor in seen:
                continue

            cast(CustomNode, MDP.get_node(neighbor)).depth = new_depth
            queue.append((neighbor, new_depth))
            seen.add(neighbor)

            if new_depth == max_depth:
                max_depth_node_names.append(neighbor)
            elif new_depth > max_depth:
                max_depth = new_depth
                max_depth_node_names = [neighbor]

    print(f"Max depth: {max_depth}")

    # Create the end node, and then create an edge from the max_depth node to
    # the end node
    MDP.add_node(CustomNode(
        name = "end",
        reward = G.end_reward,
        utility = 0, # assigned later
        is_terminal = True,
        neighbors = set(),
        level = [], # assigned later
        depth = max_depth + 1
    ))

    # add edges to the end node
    for n in max_depth_node_names:
        print(f"Adding edge: {n} -> 'end'")
        MDP.add_edge(CustomEdge(
            src=n,
            tgt="end",
            probability=[("end", 0.99), ("death", 0.01)],
            link=[]
        ))

    print("\tFirst: ", min_dist_node_name)
    print("\tLast:  ", max_depth_node_names)

    ###########################################################################
    # Make sure there is a path to the end node from wherever we are in the
    # graph
    nodes_removed = 0
    removing_nodes = True
    while removing_nodes:
        removing_nodes = False
        for node_name in nodes:
            path = bfs(MDP, node_name, "end")
            if path == None:
                nodes_removed += 1
                removing_nodes = True

                MDP.remove_node(node_name)
                nodes.remove(node_name)
                break

        progress_text(f"Nodes removed: {nodes_removed}", done=not removing_nodes)

    ###########################################################################
    # Set the reward for every node in the MDP
    max_reward = 0
    print("Updating node rewards...")
    NUM_NODES = len(MDP.nodes)
    for i, N in enumerate(MDP.nodes.values()):
        update_progress(i/NUM_NODES)

        name = N.name
        if name == 'start' or name == 'death' or name == 'end':
            continue

        N.reward = G.client.reward(N.level)
        max_reward = max(N.reward, max_reward)

    update_progress(1.0)

    for N in MDP.nodes.values():
        N.reward= -(max_reward-N.reward/max_reward)

    ###########################################################################
    # Update orientation of the levels
    if G.levels_are_horizontal:
        for node_name in MDP.nodes:
            if node_name == 'start' or node_name == 'death' or node_name == 'end':
                continue

            node = cast(CustomNode, MDP.nodes[node_name])
            node.level = columns_into_rows(node.level)

        for edge_name in MDP.edges:
            e = cast(CustomEdge, MDP.edges[edge_name])

            if len(e.link) > 0:
                e.link = columns_into_rows(e.link)

    ###########################################################################
    # Store the results because we are done
    with open(mdl_name, 'w') as f:
        f.write(MDP.to_json_string())

    print('DONE')

if __name__ == '__main__':
    start = time()
    main()
    end = time()

    print(f'Time to run: {end - start}')