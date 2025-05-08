# tests/test_topology_engine.py
from shapely.geometry import Polygon
from indoorgml_converter.engines.topology_engine import build_transitions

def test_build_transitions_touches():
    # two squares sharing an edge
    a = {"id":"a","geometry":Polygon([(0,0),(1,0),(1,1),(0,1)])}
    b = {"id":"b","geometry":Polygon([(1,0),(2,0),(2,1),(1,1)])}
    c = {"id":"c","geometry":Polygon([(2,0),(3,0),(3,1),(2,1)])}

    cell_spaces = [a,b,c]
    transitions = build_transitions(cell_spaces)

    # a and b touch, b and c touch; expect bidirectional pairs
    assert ("a","b") in transitions and ("b","a") in transitions
    assert ("b","c") in transitions and ("c","b") in transitions
    assert not any(pair[0]=="a" and pair[1]=="c" for pair in transitions)
