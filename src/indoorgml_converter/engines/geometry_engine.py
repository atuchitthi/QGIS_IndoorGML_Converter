# src/indoorgml_converter/engines/geometry_engine.py

from typing import List, Dict
from shapely.geometry.base import BaseGeometry

def build_cell_spaces(gdf) -> List[Dict]:
    """
    From a GeoDataFrame, build a list of dicts:
      { 'id': str, 'geometry': shapely.geom, 'properties': {...} }
    """
    cell_spaces = []
    for idx, row in gdf.iterrows():
        # Unique ID: use feature-id if present, otherwise index
        fid = row.get("id") or f"cell-{idx}"
        # Gather all non-geometry columns as properties
        props = {col: row[col] for col in gdf.columns if col != "geometry"}
        cell_spaces.append({
            "id": str(fid),
            "geometry": row.geometry,
            "properties": props
        })
    return cell_spaces
