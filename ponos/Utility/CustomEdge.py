from dataclasses import dataclass
from typing import Any, Dict, List
from GDM.GDM.Graph.Edge import Edge
from Utility.Link import Link

@dataclass
class CustomEdge(Edge):
    links: List[Link]

    def to_dictionary(self) -> Dict[str, Any]:
        E = super().to_dictionary()
        E['links'] = [L.to_dictionary() for L in self.links]

        return E