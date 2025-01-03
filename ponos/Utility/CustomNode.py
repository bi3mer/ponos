from dataclasses import dataclass
from typing import Any, Dict, List
from GDM.GDM.Graph.Node import Node

@dataclass
class CustomNode(Node):
    levels: List[List[str]]

    def to_dictionary(self) -> Dict[str, Any]:
        D = super().to_dictionary()
        D['levels'] = self.levels

        return D