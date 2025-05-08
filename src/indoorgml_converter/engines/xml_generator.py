# src/indoorgml_converter/engines/xml_generator.py

from xml.etree.ElementTree import Element, SubElement
from typing import List, Tuple

def generate_indoor_gml(cell_spaces: List[dict],
                        transitions: List[Tuple[str,str]]) -> Element:
    """
    Assemble the IndoorGML XML tree.
    """
    # Root with core + gml namespaces
    root = Element("IndoorGML", {
        "xmlns": "http://www.opengis.net/indoorgml/1.0/core",
        "xmlns:gml": "http://www.opengis.net/gml"
    })

    # 1) cellSpaces
    for cs in cell_spaces:
        cs_elem = SubElement(root, "cellSpace", id=cs["id"])
        geom = cs["geometry"]
        # Polygon → gml:Polygon / exterior ring
        if geom.geom_type == "Polygon":
            poly = SubElement(cs_elem, "gml:Polygon", srsName="EPSG:4326")
            exterior = SubElement(poly, "gml:exterior")
            lr = SubElement(exterior, "gml:LinearRing")
            pos = " ".join(f"{x} {y}" for x,y in geom.exterior.coords)
            SubElement(lr, "gml:posList").text = pos
        # LineString
        elif geom.geom_type == "LineString":
            line = SubElement(cs_elem, "gml:LineString", srsName="EPSG:4326")
            pos = " ".join(f"{x} {y}" for x,y in geom.coords)
            SubElement(line, "gml:posList").text = pos
        # Point
        elif geom.geom_type == "Point":
            pt = SubElement(cs_elem, "gml:Point", srsName="EPSG:4326")
            SubElement(pt, "gml:pos").text = f"{geom.x} {geom.y}"
        # (you can add Multi* or other types here)

        # semanticProperties wrapper
        if cs["properties"]:
            sem = SubElement(cs_elem, "semanticProperties")
            for k,v in cs["properties"].items():
                p = SubElement(sem, k)
                p.text = str(v)

    # 2) transitions
    for frm, to in transitions:
        tr = SubElement(root, "cellSpaceTransition", id=f"trans-{frm}-{to}")
        SubElement(tr, "connects", cellSpaceFrom=frm, cellSpaceTo=to)

    return root
