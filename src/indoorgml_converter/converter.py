import logging
import re
import math
from pathlib import Path
from xml.etree.ElementTree import ElementTree

import pandas as pd

from .io_utils import load_features
from .engines.geometry_engine import build_cell_spaces
from .engines.topology_engine import build_transitions
from .engines.semantic_engine import attach_semantics
from .engines.xml_generator import generate_indoor_gml
from .visualizer import visualize

logger = logging.getLogger(__name__)
# matches "1st", "2nd", "3rd", "4th", "-1st", etc.
_ORD = re.compile(r'^\s*(\-?\d+)(?:st|nd|rd|th)?\s*$', re.IGNORECASE)


def _normalize_floor(v) -> str:
    """Turn various floor labels into a canonical single token."""
    s = str(v).strip()
    low = s.lower()
    if low in ('b', 'basement', '-1'):
        return 'B'
    if low in ('g', 'ground', '0'):
        return 'G'
    m = _ORD.match(s)
    if m:
        return m.group(1)
    return s or 'None'


def detect_level(props: dict) -> str:
    """
    Detect the floor of a space by collecting *all* possible indicators:
      1) explicit keys: floor_name, level_name, level, floor
      1a) explicit min_level & max_level
      2) numeric z property: <0 → B, 0 → G, >0 → int(z)
      3) any key containing: elevation, storey, story, z
      4) any ordinal-like string value
    Normalize, dedupe, then:
      • if exactly one unique value → return it
      • if multiple → log a warning & pick the first
      • if none → return 'None'
    """
    logger.debug(f"detect_level props: {props!r}")
    candidates = []

    # 1) explicit floor props (skip None or nan)
    for key in ('floor_name', 'level_name', 'level', 'floor'):
        v = props.get(key)
        if v is None or (isinstance(v, float) and math.isnan(v)):
            continue
        candidates.append(_normalize_floor(v))

    # 1a) explicit min/max level
    lowv = props.get('min_level')
    highv = props.get('max_level')
    if lowv is not None and highv is not None \
       and not (isinstance(lowv, float) and math.isnan(lowv)) \
       and not (isinstance(highv, float) and math.isnan(highv)):
        return f"{_normalize_floor(lowv)}-{_normalize_floor(highv)}"

    # 2) numeric z overrides everything (skip nan)
    vz = props.get('z')
    if isinstance(vz, (int, float)) and not (isinstance(vz, float) and math.isnan(vz)):
        if vz < 0:
            return 'B'
        if vz == 0:
            return 'G'
        return str(int(vz))

    # 3) substring-based keys (skip None or nan)
    for k, v in props.items():
        if v is None or (isinstance(v, float) and math.isnan(v)):
            continue
        kl = k.lower()
        if any(w in kl for w in ('elevation', 'storey', 'story', 'z')):
            candidates.append(_normalize_floor(v))

    # 4) catch any ordinal-like string
    for k, v in props.items():
        if v is None or (isinstance(v, float) and math.isnan(v)):
            continue
        m = _ORD.match(str(v))
        if m:
            candidates.append(m.group(1))

    # dedupe while preserving order
    unique = list(dict.fromkeys(candidates))
    if not unique:
        logger.debug("No floor info found → 'None'")
        return 'None'
    if len(unique) > 1:
        logger.warning("Conflicting floor values %s; choosing %s", unique, unique[0])
    return unique[0]


def print_adjacency(cell_spaces, transitions):
    adj = {cs['id']: [] for cs in cell_spaces}
    for a, b in transitions:
        adj[a].append(b)
    df = pd.DataFrame([
        {'Room': r, 'Neighbors': ",".join(ns) or "-"}
        for r, ns in adj.items()
    ])
    print("\n=== Adjacency ===")
    print(df.to_string(index=False))
    return df


def print_features(cell_spaces, transitions):
    nbrs = {cs['id']: [] for cs in cell_spaces}
    for a, b in transitions:
        nbrs[a].append(b)
    rows = []
    for cs in cell_spaces:
        fid, props = cs['id'], cs['properties']
        lvl = detect_level(props)
        rows.append({
            'ID': fid,
            'Level': lvl,
            'Name': props.get('name', '-'),
            'Neighbors': ",".join(nbrs[fid]) or "-"
        })
    df = pd.DataFrame(rows)
    print("\n=== Features ===")
    print(df.to_string(index=False))
    return df


def convert(geojson_path: Path,
            output_path: Path,
            visualize_output: bool = True) -> bool:
    try:
        logger.info("Loading GeoJSON from %s", geojson_path)
        gdf = load_features(geojson_path)

        logger.info("Building %d cell-spaces", len(gdf))
        cell_spaces = build_cell_spaces(gdf)

        logger.info("Attaching semantics")
        attach_semantics(cell_spaces)

        logger.info("Building transitions")
        transitions = build_transitions(cell_spaces)

        logger.info("Generating IndoorGML XML")
        root = generate_indoor_gml(cell_spaces, transitions)
        tree = ElementTree(root)
        tree.write(output_path, encoding="utf-8", xml_declaration=True)
        print(f"\nConverted → {output_path}")

        print_adjacency(cell_spaces, transitions)
        print_features(cell_spaces, transitions)

        if visualize_output:
            logger.info("Launching floor-by-floor preview")
            visualize(cell_spaces, transitions)

        logger.info("✅ Conversion complete")
        return True

    except Exception:
        logger.exception("❌ Conversion error")
        return False

# # src/indoorgml_converter/converter.py
#
# import logging
# import re
# import math
# from pathlib import Path
# from xml.etree.ElementTree import ElementTree
#
# import pandas as pd
#
# from .io_utils import load_features
# from .engines.geometry_engine import build_cell_spaces
# from .engines.topology_engine import build_transitions
# from .engines.semantic_engine import attach_semantics
# from .engines.xml_generator import generate_indoor_gml
# from .visualizer import visualize
#
# logger = logging.getLogger(__name__)
#
# # matches "1st", "2nd", "3rd", "4th", "-1st", etc.
# _ORD = re.compile(r'^\s*(\-?\d+)(?:st|nd|rd|th)?\s*$', re.IGNORECASE)
#
#
# def _normalize_floor(v) -> str:
#     """Turn various floor labels into a canonical single token."""
#     s = str(v).strip()
#     low = s.lower()
#     if low in ('b', 'basement', '-1'):
#         return 'B'
#     if low in ('g', 'ground', '0'):
#         return 'G'
#     m = _ORD.match(s)
#     if m:
#         return m.group(1)
#     return s or 'None'
#
#
# def detect_level(props: dict) -> str:
#     """
#     Detect the floor of a space by collecting *all* possible indicators:
#       1) explicit keys: floor_name, level_name, level, floor
#       2) numeric z property: <0 → B, 0 → G, >0 → int(z)
#       3) any key containing: elevation, storey, story, z (string)
#       4) any ordinal-like string value
#     Normalize, dedupe, then:
#       • if exactly one unique value → return it
#       • if multiple → log a warning & pick the first
#       • if none → return 'None'
#     """
#     logger.debug(f"detect_level props: {props!r}")
#     candidates = []
#
#     # 1) explicit floor props (skip None or nan)
#     for key in ('floor_name', 'level_name', 'level', 'floor'):
#         v = props.get(key)
#         if v is None or (isinstance(v, float) and math.isnan(v)):
#             continue
#         candidates.append(_normalize_floor(v))
#
#     # 2) numeric z overrides everything (skip nan)
#     vz = props.get('z')
#     if isinstance(vz, (int, float)) and not (isinstance(vz, float) and math.isnan(vz)):
#         if vz < 0:
#             return 'B'
#         if vz == 0:
#             return 'G'
#         return str(int(vz))
#
#     # 3) substring-based keys (skip None or nan)
#     for k, v in props.items():
#         if v is None or (isinstance(v, float) and math.isnan(v)):
#             continue
#         kl = k.lower()
#         if any(w in kl for w in ('elevation', 'storey', 'story', 'z')):
#             candidates.append(_normalize_floor(v))
#
#     # 4) catch any ordinal-like string
#     for k, v in props.items():
#         if v is None or (isinstance(v, float) and math.isnan(v)):
#             continue
#         m = _ORD.match(str(v))
#         if m:
#             candidates.append(m.group(1))
#
#     # dedupe while preserving order
#     unique = list(dict.fromkeys(candidates))
#     if not unique:
#         logger.debug("No floor info found → 'None'")
#         return 'None'
#     if len(unique) > 1:
#         logger.warning("Conflicting floor values %s; choosing %s", unique, unique[0])
#     return unique[0]
#
#
# def print_adjacency(cell_spaces, transitions):
#     adj = {cs['id']: [] for cs in cell_spaces}
#     for a, b in transitions:
#         adj[a].append(b)
#     df = pd.DataFrame([
#         {'Room': r, 'Neighbors': ",".join(ns) or "-"}
#         for r, ns in adj.items()
#     ])
#     print("\n=== Adjacency ===")
#     print(df.to_string(index=False))
#     return df
#
#
# def print_features(cell_spaces, transitions):
#     nbrs = {cs['id']: [] for cs in cell_spaces}
#     for a, b in transitions:
#         nbrs[a].append(b)
#     rows = []
#     for cs in cell_spaces:
#         fid, props = cs['id'], cs['properties']
#         lvl = detect_level(props)
#         rows.append({
#             'ID': fid,
#             'Level': lvl,
#             'Name': props.get('name', '-'),
#             'Neighbors': ",".join(nbrs[fid]) or "-"
#         })
#     df = pd.DataFrame(rows)
#     print("\n=== Features ===")
#     print(df.to_string(index=False))
#     return df
#
#
# def convert(geojson_path: Path,
#             output_path: Path,
#             visualize_output: bool = True) -> bool:
#     try:
#         logger.info("Loading GeoJSON from %s", geojson_path)
#         gdf = load_features(geojson_path)
#
#         logger.info("Building %d cell-spaces", len(gdf))
#         cell_spaces = build_cell_spaces(gdf)
#
#         logger.info("Attaching semantics")
#         attach_semantics(cell_spaces)
#
#         logger.info("Building transitions")
#         transitions = build_transitions(cell_spaces)
#
#         logger.info("Generating IndoorGML XML")
#         root = generate_indoor_gml(cell_spaces, transitions)
#         tree = ElementTree(root)
#         tree.write(output_path, encoding="utf-8", xml_declaration=True)
#         print(f"\nConverted → {output_path}")
#
#         print_adjacency(cell_spaces, transitions)
#         print_features(cell_spaces, transitions)
#
#         if visualize_output:
#             logger.info("Launching floor-by-floor preview")
#             visualize(cell_spaces, transitions)
#
#         logger.info("✅ Conversion complete")
#         return True
#
#     except Exception:
#         logger.exception("❌ Conversion error")
#         return False
