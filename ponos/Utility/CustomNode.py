from dataclasses import dataclass
from typing import Any, Dict, List
from GDM.GDM.Graph.Node import Node

@dataclass
class CustomNode(Node):
    level: List[str]
    depth: int

    def to_dictionary(self) -> Dict[str, Any]:
        D = super().to_dictionary()
        D['level'] = self.level
        D['depth'] = self.depth

        return D