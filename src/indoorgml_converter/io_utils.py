# src/indoorgml_converter/io_utils.py

import geopandas as gpd
from pathlib import Path

def load_features(path: Path) -> gpd.GeoDataFrame:
    """
    Read ANY GeoJSON into a GeoDataFrame, explode multi-geometries
    so each row has a single geometry.
    """
    gdf = gpd.read_file(str(path))
    # explode returns a GeoDataFrame with each geometry primitive in its own row
    try:
        gdf = gdf.explode(index_parts=False).reset_index(drop=True)
    except TypeError:
        # older geopandas API
        gdf = gdf.explode().reset_index(drop=True)
    return gdf
