# src/indoorgml_converter/engines/topology_engine.py

from typing import List, Tuple

def build_transitions(cell_spaces) -> List[Tuple[str,str]]:
    """
    Build a list of (from_id, to_id) whenever two cellSpaces touch.
    """
    transitions = []
    n = len(cell_spaces)
    for i in range(n):
        for j in range(i+1, n):
            a = cell_spaces[i]
            b = cell_spaces[j]
            if a["geometry"].touches(b["geometry"]):
                transitions.append((a["id"], b["id"]))
                transitions.append((b["id"], a["id"]))
    return transitions
