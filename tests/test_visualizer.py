# tests/test_visualizer.py
import pytest

from indoorgml_converter.visualizer import determine_feature_type

@pytest.mark.parametrize("props,expected", [
    ({"name":"Main Door","feature":"door"}, "door"),
    ({"name":"Entrance hall","foo":"exit"}, "door"),
    ({"name":"Corridor","foo":"passage"}, "corridor"),
    ({"name":"Stairs up"}, "stairs"),
    ({"foo":"elevator"}, "elevator"),
    ({}, "room"),
])
def test_determine_feature_type(props, expected):
    assert determine_feature_type(props) == expected
