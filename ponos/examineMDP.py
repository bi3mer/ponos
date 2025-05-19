import json
import sys
import os

from GDM.GDM.Graph import Graph
from Utility.CustomNode import CustomNode
from Utility.CustomEdge import CustomEdge
from GDM.GDM.utility import bfs

file_path = sys.argv[1]
if not os.path.exists(file_path):
    print("Error! Graph file provided does not exist!")
    exit(1)

with open(file_path, "r") as f:
    graph = json.load(f)

MDP = Graph()
MDP.add_default_node(node_name="start", terminal=True, reward=0.0)
MDP.add_default_node(node_name="death", terminal=True, reward=-1)

for n in graph['nodes']:
    name = n['name']
    if name == 'start' or name == 'death':
        continue


    MDP.add_node(CustomNode(
        name = name,
        reward = n['reward'], # assigned later
        utility = 0, # assigned later
        is_terminal = False,
        neighbors = set(),
        level = n['levels'],
        depth = n['depth']   # assigned later
    ))

for e in graph['edges']:
    MDP.add_edge(CustomEdge(
        src=e['src'],
        tgt=e['tgt'],
        probability=e['probability'],
        link=e['links']
    ))

# All nodes must have a path to the start node
nodes_removed = 0
removing_nodes = True
nodes = list(MDP.nodes.keys())
nodes.remove("start")
nodes.remove("end")
nodes.remove("death")

while removing_nodes:
    removing_nodes = False
    for node_name in nodes:
        path = bfs(MDP, "start", node_name)
        if path == None:
            nodes_removed += 1
            removing_nodes = True

            print(f'removed: {node_name}')
            MDP.remove_node(node_name)
            nodes.remove(node_name)
            break

print(f"Nodes without a path to start: {nodes_removed}")
print(f"Nodes left: {len(MDP.nodes)}")

# Find the node that is furthest from the start node
max_depth = 0
max_dist_node_names = []
seen = set()
seen.add("start")
queue = [("start", 0)]

while len(queue) > 0:
    node_name, depth = queue.pop(0)
    new_depth = depth + 1

    for neighbor in MDP.neighbors(node_name):
        if neighbor in seen:
            continue

        queue.append((neighbor, new_depth))
        seen.add(neighbor)

        if new_depth == max_depth:
            max_dist_node_names.append(neighbor)
        elif new_depth > max_depth:
            max_depth = new_depth
            max_dist_node_names = [neighbor]

print(f"Node furthest from the start: {max_dist_node_names}, {max_depth}")

## make them the end node

# edges to the end node
for n in max_dist_node_names:
    print(f"Adding edge: {n} -> 'end'")
    MDP.add_edge(CustomEdge(
        src=n,
        tgt="end",
        probability=[("end", 0.99), ("death", 0.01)],
        link=[]
    ))

# Make sure there is a path to the end node from wherever we are in the graph
nodes_removed = 0
removing_nodes = True
while removing_nodes:
    removing_nodes = False
    for node_name in nodes:
        path = bfs(MDP, node_name, "end")
        if path == None:
            nodes_removed += 1
            removing_nodes = True

            print(f'removed: {node_name}')
            MDP.remove_node(node_name)
            nodes.remove(node_name)
            break

print(f"Nodes without a path to 'end': {nodes_removed}")
print(f"Nodes left: {len(MDP.nodes)}")