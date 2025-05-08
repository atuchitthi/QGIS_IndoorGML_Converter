# tests/test_converter.py
import math
import pandas as pd
import pytest
from shapely.geometry import Point, Polygon

from indoorgml_converter.converter import (
    _normalize_floor,
    detect_level,
    print_adjacency,
    print_features,
)

def test_normalize_floor_basement_and_ground():
    assert _normalize_floor('B') == 'B'
    assert _normalize_floor('basement') == 'B'
    assert _normalize_floor('-1') == 'B'
    assert _normalize_floor('G') == 'G'
    assert _normalize_floor('ground') == 'G'
    assert _normalize_floor('0') == 'G'

def test_normalize_floor_ordinals_and_numbers():
    assert _normalize_floor('1st') == '1'
    assert _normalize_floor('2nd') == '2'
    assert _normalize_floor('3rd') == '3'
    assert _normalize_floor('10th') == '10'
    # unknown string passes through
    assert _normalize_floor('Mezzanine') == 'Mezzanine'

@pytest.mark.parametrize("props,expected", [
    ({'floor_name':'2nd'}, '2'),
    ({'level':'3rd'}, '3'),
    ({'floor':'Ground'}, 'G'),
    ({'min_level':'1st','max_level':'3rd'}, '1-3'),
    ({'elevation':'5th'}, '5'),
    ({'storey': 'Basement'}, 'B'),
    ({'z': -1}, 'B'),
    ({'z': 0}, 'G'),
    ({'z': 7}, '7'),
    ({'some_key': '4th'}, '4'),
    ({}, 'None'),
])
def test_detect_level_various(props, expected):
    assert detect_level(props) == expected

def test_detect_level_conflict_logs_and_picks_first(caplog):
    # both floor_name and level provided
    props = {'floor_name':'1st','level':'2nd'}
    caplog.set_level('WARNING')
    lvl = detect_level(props)
    assert lvl == '1'
    assert 'Conflicting floor values' in caplog.text

def test_print_adjacency_and_features(tmp_path, capsys):
    # two cell_spaces a and b, with one transition
    cell_spaces = [
        {'id':'a','properties':{}},
        {'id':'b','properties':{}},
    ]
    transitions = [('a','b'), ('b','a')]
    adj_df = print_adjacency(cell_spaces, transitions)
    feat_df = print_features(cell_spaces, transitions)

    # adjacency DataFrame
    assert list(adj_df.columns) == ['Room','Neighbors']
    row_a = adj_df[adj_df.Room=='a'].iloc[0]
    assert row_a.Neighbors == 'b'
    # features DataFrame
    assert 'ID' in feat_df.columns and 'Level' in feat_df.columns
    assert set(feat_df['ID']) == {'a','b'}
    # capture printed output contains headers
    out = capsys.readouterr().out
    assert '=== Adjacency ===' in out
    assert '=== Features ===' in out
