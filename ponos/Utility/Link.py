from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Link:
    src_segment_index: int
    tgt_segment_index: int
    link: List[str]

    def to_dictionary(self) -> Dict[str, Any]:
        return {
            'src-index': self.src_segment_index,
            'tgt-index': self.tgt_segment_index,
            'link': self.link
        }