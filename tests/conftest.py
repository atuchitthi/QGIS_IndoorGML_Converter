# tests/conftest.py

import pytest
from pathlib import Path

def _copy_geojson(src_name: str, tmp_path) -> str:
    """
    Copy a GeoJSON named `src_name` from resources/ into tmp_path
    and return its filesystem path as a string.
    """
    repo_root = Path(__file__).parent.parent
    src = repo_root / "resources" / src_name
    if not src.exists():
        pytest.skip(f"Missing GeoJSON fixture {src_name} at {src}")
    dst = tmp_path / src_name
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return str(dst)

@pytest.fixture
def sample_geojson(tmp_path):
    """A small, known-good GeoJSON for converter tests."""
    # assumes you have resources/sample.geojson
    return _copy_geojson("sample.geojson", tmp_path)

@pytest.fixture
def building_geojson(tmp_path):
    """Your larger building_sample.geojson for integration tests."""
    # assumes you have resources/building_sample.geojson
    return _copy_geojson("building_sample.geojson", tmp_path)
