from dataclasses import dataclass
from typing import Any, Dict, List
from GDM.GDM.Graph.Edge import Edge

@dataclass
class CustomEdge(Edge):
    link: List[str]

    def to_dictionary(self) -> Dict[str, Any]:
        E = super().to_dictionary()
        E['link'] = self.link

        return E