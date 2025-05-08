# tests/test_io_utils.py
import json
import geopandas as gpd
from shapely.geometry import Point
import pytest

from indoorgml_converter.io_utils import load_features

def test_load_features_creates_geodataframe(tmp_path):
    # write minimal GeoJSON
    data = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {"id": "pt1", "foo": "bar"},
            "geometry": {"type": "Point", "coordinates": [1.0, 2.0]}
        }]
    }
    f = tmp_path / "test.geojson"
    f.write_text(json.dumps(data))

    gdf = load_features(f)
    assert isinstance(gdf, gpd.GeoDataFrame)
    assert "geometry" in gdf
    assert list(gdf.geometry)[0].equals(Point(1.0, 2.0))
    assert gdf.loc[0, "foo"] == "bar"
