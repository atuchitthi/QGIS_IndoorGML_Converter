# tests/test_geometry_engine.py
import geopandas as gpd
from shapely.geometry import Point, Polygon
from indoorgml_converter.engines.geometry_engine import build_cell_spaces

def test_build_cell_spaces_from_gdf(tmp_path):
    # create simple GeoDataFrame
    df = gpd.GeoDataFrame([
        {"id":"p","foo":123, "geometry": Point(0,0)},
        {"id":"poly","foo":456, "geometry": Polygon([(0,0),(1,0),(1,1),(0,1)])},
    ], geometry="geometry")

    cs = build_cell_spaces(df)
    assert isinstance(cs, list) and len(cs) == 2

    ids = {c["id"] for c in cs}
    assert ids == {"p","poly"}

    entry = next(c for c in cs if c["id"]=="p")
    assert entry["properties"]["foo"] == 123
    assert entry["geometry"].equals(Point(0,0))
