# tests/test_xml_generator.py
import xml.etree.ElementTree as ET
from shapely.geometry import Point, Polygon
from indoorgml_converter.engines.xml_generator import generate_indoor_gml

def test_generate_indoor_gml_basic():
    cell_spaces = [
        {"id":"r1","geometry":Polygon([(0,0),(1,0),(1,1),(0,1)]),"properties":{"id":"r1","floor":"1"}},
    ]
    transitions = []
    root = generate_indoor_gml(cell_spaces, transitions)
    assert isinstance(root, ET.Element)
    # should contain IndoorFeatures or similar tag
    assert root.tag.endswith("IndoorFeatures")
    # check our r1 appears in XML
    xml_str = ET.tostring(root, encoding="unicode")
    assert "r1" in xml_str
