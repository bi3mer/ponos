from dataclasses import dataclass
from typing import List, Optional
from GDM.GDM.Graph.Edge import Edge

@dataclass
class CustomEdge(Edge):
    link: Optional[List[str]]