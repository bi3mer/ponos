from dataclasses import dataclass
from typing import List
from GDM.GDM.Graph.Node import Node

@dataclass
class CustomNode(Node):
    level: List[str]